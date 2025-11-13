#!/usr/bin/env python3
import os
import time
import requests
import socket
import argparse

# CONFIG
API_BASE = "http://127.0.0.1:8000"

def register_agent(pid):
    info = {
        "pid": pid,
        "start_time": time.time(),
        "hostname": socket.gethostname()
    }
    try:
        res = requests.post(f"{API_BASE}/agent/register", json=info, timeout=2)
        print(f"[AGENT] Registered: {res.status_code}")
    except Exception as e:
        print(f"[AGENT] Registration failed: {e}")

def post_incident(pid, parent_pid, cmd, user, action):
    record = {
        "pid": pid,
        "timestamp": time.time(),
        "action": action,
        "command_line": cmd,
        "user": user,
        "details": {"parent_pid": parent_pid}
    }
    try:
        res = requests.post(f"{API_BASE}/forensics/", json=record, timeout=2)
        print(f"[LOG] Incident posted: {action} (PID {pid})")
    except Exception as e:
        print(f"[LOG] Incident failed: {e}")

def add_baseline_entry(exec_path, user, fingerprint):
    entry = {
        "exec_path": exec_path,
        "user": user,
        "fingerprint": fingerprint
    }
    try:
        res = requests.post(f"{API_BASE}/baseline/entry", json=entry, timeout=2)
        print(f"[BASELINE] Added entry: {exec_path}")
    except Exception as e:
        print(f"[BASELINE] Add failed: {e}")

def get_policy():
    try:
        res = requests.get(f"{API_BASE}/baseline/policy", timeout=2)
        return res.json()
    except Exception as e:
        print(f"[POLICY] Get failed: {e}")
        return None

def get_child_pids(target_pid):
    # Returns a set of child PIDs of the given PID (Linux /proc-based)
    children = set()
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/stat') as f:
                    stat = f.read().split()
                    ppid = int(stat[3])
                    if ppid == target_pid:
                        children.add(int(pid))
            except Exception:
                continue
    return children

def get_command_line(pid):
    try:
        with open(f'/proc/{pid}/cmdline', 'rb') as f:
            raw = f.read().replace(b'\x00', b' ').decode().strip()
            return raw if raw else "[unknown command]"
    except Exception:
        return "[unreadable]"

def get_user(pid):
    try:
        import pwd
        stat_info = os.stat(f"/proc/{pid}")
        return pwd.getpwuid(stat_info.st_uid).pw_name
    except Exception:
        return "[unknown_user]"

def agent_monitor(monitor_pid, learn_mode=True, interval=1, contain_mode=False):
    print(f"[AGENT] Starting monitor for PID {monitor_pid} (learn_mode={learn_mode}, contain={contain_mode}, interval={interval}s)")
    register_agent(os.getpid())
    seen = set()
    while True:
        children = get_child_pids(monitor_pid)
        new_children = children - seen
        if new_children:
            policy = get_policy()
        for child in new_children:
            cmd = get_command_line(child)
            user = get_user(child)
            print(f"[DETECT] New child found: PID {child} CMD '{cmd}' USER {user}")
            if learn_mode:
                add_baseline_entry(exec_path=cmd.split()[0], user=user, fingerprint=cmd)
                post_incident(child, monitor_pid, cmd, user, "baseline_add")
            else:
                blocked = policy and any(blk in cmd for blk in policy.get("block", []))
                allowed = policy and any(allow in cmd for allow in policy.get("allow", []))
                if blocked:
                    print(f"[ACTION] Blocking & killing PID {child}: '{cmd}'")
                    post_incident(child, monitor_pid, cmd, user, "kill_blocked")
                    if contain_mode:
                        try:
                            os.kill(child, 9)
                        except Exception as e:
                            print(f"[ERROR] Kill failed: {e}")
                elif allowed:
                    print(f"[ACTION] Allowed: {cmd}")
                    post_incident(child, monitor_pid, cmd, user, "allow")
                else:
                    print(f"[ACTION] Alert: unknown/uncategorized: {cmd}")
                    post_incident(child, monitor_pid, cmd, user, "alert")
        seen = children
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="REFLEX Autonomous Security Agent")
    parser.add_argument('--monitor-pid', type=int, required=True, help='PID to monitor')
    parser.add_argument('--learn', action='store_true', help='Enable baseline learning mode')
    parser.add_argument('--interval', type=float, default=1.0, help='Polling interval (seconds)')
    parser.add_argument('--contain', action='store_true', help='Actually kill blocked PIDs')
    args = parser.parse_args()
    agent_monitor(
        monitor_pid=args.monitor_pid,
        learn_mode=args.learn,
        interval=args.interval,
        contain_mode=args.contain
    )
def get_full_forensics(pid):
    forensics = {}
    # Command line
    forensics["cmdline"] = get_command_line(pid)
    # CWD
    try:
        forensics["cwd"] = os.readlink(f"/proc/{pid}/cwd")
    except Exception:
        forensics["cwd"] = "[unreadable]"
    # Environ
    try:
        with open(f"/proc/{pid}/environ", 'rb') as f:
            forensics["environ"] = f.read().replace(b'\x00', b'\n').decode()
    except Exception:
        forensics["environ"] = "[unreadable]"
    # Parent command
    try:
        with open(f"/proc/{pid}/stat") as f:
            stat = f.read().split()
            ppid = int(stat[3])
            forensics["parent_pid"] = ppid
            forensics["parent_cmd"] = get_command_line(ppid)
    except Exception:
        forensics["parent_pid"] = -1
        forensics["parent_cmd"] = "[unreadable]"
    # Ancestry (grandparents)
    ancestry = []
    curr = pid
    try:
        while curr != 1 and curr > 0:
            with open(f"/proc/{curr}/stat") as f:
                stat = f.read().split()
                ppid = int(stat[3])
                ancestry.append(ppid)
                curr = ppid
    except Exception:
        pass
    forensics["ancestry"] = ancestry
    return forensics

def post_incident(pid, parent_pid, cmd, user, action):
    # Use advanced forensics
    forensics = get_full_forensics(pid)
    record = {
        "pid": pid,
        "timestamp": time.time(),
        "action": action,
        "command_line": cmd,
        "user": user,
        "details": {"parent_pid": parent_pid, "forensics": forensics}
    }
    try:
        res = requests.post(f"{API_BASE}/forensics/", json=record, timeout=2)
        print(f"[LOG] Incident posted: {action} (PID {pid})")
    except Exception as e:
        print(f"[LOG] Incident failed: {e}")
