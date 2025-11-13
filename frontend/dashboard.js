// REFLEX Dashboard - Complete Fixed Version v3.0
const API = "https://reflex-soc.onrender.com";
let CURRENT_ORG = "default_org";
let CURRENT_USER = null;

// ------- LOGIN -------
function login(username, password) {
  console.log("Login attempt:", username, password, CURRENT_ORG);
  fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      username: username, 
      password: password, 
      org_id: CURRENT_ORG 
    })
  })
    .then(res => res.json())
    .then(data => {
      console.log("Login response:", data);
      if (data.token) {
        CURRENT_USER = { 
          role: data.role, 
          org_id: data.org_id, 
          username: data.username,
          token: data.token
        };
        localStorage.setItem("auth_token", data.token);
        document.getElementById("user-info").innerHTML = 
          `✅ Logged in as <b>${data.username}</b> (${data.role})`;
        loadDashboard();
        alert(`✅ Login successful as ${data.username}!`);
      } else {
        alert("❌ Login failed: " + (data.detail || "Invalid credentials"));
      }
    })
    .catch(err => {
      console.error("Login error:", err);
      alert("❌ Login error: " + err.message);
    });
}

// ------- AGENT ONLINE -------
function loadAgents() {
  fetch(`${API}/agent/online?org_id=${CURRENT_ORG}`)
    .then(res => res.json())
    .then(agents => {
      const cont = document.getElementById("agents-online");
      if (!cont) return;
      if (!agents || !agents.length) {
        cont.innerHTML = "<b>No agents online</b>";
        return;
      }
      cont.innerHTML = agents.map(a => `
        <div class="agent-card">
          <b>${a.agent_id}</b> (${a.hostname})<br>
          Status: ${a.status} | IP: ${a.ip}
        </div>
      `).join("");
    })
    .catch(err => {
      const cont = document.getElementById("agents-online");
      if (cont) cont.innerHTML = "<b>Error loading agents</b>";
    });
}

// ------- EVENTS -------
function loadEvents() {
  fetch(`${API}/agent/events?org_id=${CURRENT_ORG}`)
    .then(res => res.json())
    .then(events => {
      const cont = document.getElementById("live-events");
      if (!cont) return;
      if (!events || !events.length) {
        cont.innerHTML = "<b>No events</b>";
        return;
      }
      cont.innerHTML = events.reverse().slice(0, 5).map(e => `
        <div class="event-entry ${e.threat_score > 60 ? 'threat-high' : ''}">
          <b>[${e.event_type}]</b> Threat: ${e.threat_score || 0}<br>
          ${new Date(e.timestamp * 1000).toLocaleTimeString()}
        </div>
      `).join("");
    })
    .catch(err => {
      const cont = document.getElementById("live-events");
      if (cont) cont.innerHTML = "<b>Error loading events</b>";
    });
}

// ------- INCIDENT LOG -------
function loadIncidents() {
  fetch(`${API}/forensics/`)
    .then(res => res.json())
    .then(logs => {
      const logCont = document.getElementById("logs");
      if (!logCont) return;
      if (!logs || !logs.length) {
        logCont.innerHTML = "<b>No incidents yet</b>";
        return;
      }
      logCont.innerHTML = logs.map(l => `
        <div class="log-entry">
          <b>${l.summary || "Incident"}</b> (${l.type || ""})<br>
          Time: ${l.created || ""} | File: ${l.file_path || ""}
        </div>
      `).join("");
    })
    .catch(() => {
      const logCont = document.getElementById("logs");
      if (logCont) logCont.innerHTML = "<b>Error loading logs</b>";
    });
}

// ------- POLICY DISPLAY -------
function loadPolicy() {
  fetch(`${API}/baseline/policy`)
    .then(res => res.json())
    .then(policy => {
      const cont = document.getElementById("policy");
      if (cont) {
        cont.innerHTML = `
          <b>Allow:</b> ${policy.allow.join(", ")}<br>
          <b>Block:</b> ${policy.block.join(", ")}
        `;
      }
    })
    .catch(() => {
      const cont = document.getElementById("policy");
      if (cont) cont.innerHTML = "<b>Error loading policy</b>";
    });
}

// ------- ADD BLOCK (FIXED) -------
function addBlock() {
  let val = document.getElementById("blockInput").value.trim();
  if (!val) {
    alert("❌ Please enter a keyword to block");
    return;
  }
  
  fetch(`${API}/baseline/policy`)
    .then(res => res.json())
    .then(policy => {
      if (!policy.block) policy.block = [];
      policy.block.push(val);
      
      fetch(`${API}/baseline/policy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(policy)
      })
        .then(res => res.json())
        .then(data => {
          alert(`✅ Added block for: ${val}`);
          loadPolicy();
          document.getElementById("blockInput").value = "";
        })
        .catch(err => alert("❌ Failed to add block: " + err));
    })
    .catch(err => alert("❌ Failed to load policy: " + err));
}

// ------- AUTO-RESPONSE PLAYBOOKS -------
function loadPlaybooks() {
  fetch(`${API}/response/playbooks?org_id=${CURRENT_ORG}`)
    .then(res => res.json())
    .then(playbooks => {
      const cont = document.getElementById("playbooks");
      if (!cont) return;
      if (!playbooks || !playbooks.length) {
        cont.innerHTML = "<b>No playbooks configured</b>";
        return;
      }
      cont.innerHTML = playbooks.map(pb => `
        <div class="playbook-card">
          <b>${pb.name}</b><br>
          Trigger: ${pb.trigger_severity} | Status: ${pb.enabled ? "✅" : "❌"}<br>
          <button onclick="executePlaybook('${pb.playbook_id}', 1)">Execute</button>
        </div>
      `).join("");
    })
    .catch(err => {
      const cont = document.getElementById("playbooks");
      if (cont) cont.innerHTML = "<b>Error loading playbooks</b>";
    });
}

// ------- EXECUTE PLAYBOOK -------
function executePlaybook(playbookId, incidentId) {
  fetch(`${API}/response/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      playbook_id: playbookId, 
      incident_id: incidentId,
      org_id: CURRENT_ORG 
    })
  })
    .then(res => res.json())
    .then(result => {
      alert(`✅ Playbook executed: ${result.execution_id}`);
      loadExecutionLogs();
    })
    .catch(err => alert("❌ Error executing playbook: " + err));
}

// ------- EXECUTION LOGS -------
function loadExecutionLogs() {
  fetch(`${API}/response/logs?org_id=${CURRENT_ORG}`)
    .then(res => res.json())
    .then(logs => {
      const cont = document.getElementById("execution-logs");
      if (!cont) return;
      if (!logs || !logs.length) {
        cont.innerHTML = "<b>No executions yet</b>";
        return;
      }
      cont.innerHTML = logs.reverse().slice(0, 5).map(log => `
        <div class="log-entry">
          <b>Exec: ${log.execution_id}</b><br>
          Incident #${log.incident_id}<br>
          ${new Date(log.timestamp * 1000).toLocaleTimeString()}
        </div>
      `).join("");
    })
    .catch(err => {
      const cont = document.getElementById("execution-logs");
      if (cont) cont.innerHTML = "<b>Error loading logs</b>";
    });
}

// ------- AI INCIDENTS -------
function loadAIIncidents() {
  fetch(`${API}/agent/incidents`)
    .then(res => res.json())
    .then(incidents => {
      const cont = document.getElementById("ai-incidents");
      if (!cont) return;
      if (!incidents || !incidents.length) {
        cont.innerHTML = "<b>No incidents detected</b>";
        return;
      }
      cont.innerHTML = incidents.reverse().slice(0, 5).map(inc => `
        <div class="incident-card">
          <b>Incident #${inc.incident_id}</b><br>
          Severity: ${inc.severity} | Events: ${inc.event_count}
        </div>
      `).join("");
    })
    .catch(err => {
      const cont = document.getElementById("ai-incidents");
      if (cont) cont.innerHTML = "<b>Error loading incidents</b>";
    });
}

// ------- INTEGRATION STATUS -------
function loadIntegrationHealth() {
  fetch(`${API}/integrations/health`)
    .then(res => res.json())
    .then(health => {
      const cont = document.getElementById("integration-status");
      if (!cont) return;
      cont.innerHTML = Object.entries(health).map(([service, data]) => `
        <div class="integration-card">
          <b>${service.toUpperCase()}</b> - ${data.status === 'connected' ? '✅' : '❌'}<br>
          Last: ${new Date(data.last_action * 1000).toLocaleTimeString()}
        </div>
      `).join("");
    })
    .catch(err => {
      const cont = document.getElementById("integration-status");
      if (cont) cont.innerHTML = "<b>Integrations unavailable</b>";
    });
}

// ------- INTEGRATION LOGS -------
function loadIntegrationLogs() {
  fetch(`${API}/integrations/logs?limit=10`)
    .then(res => res.json())
    .then(logs => {
      const cont = document.getElementById("integration-logs");
      if (!cont) return;
      if (!logs || !logs.length) {
        cont.innerHTML = "<b>No integration actions yet</b>";
        return;
      }
      cont.innerHTML = logs.reverse().slice(0, 5).map(log => `
        <div class="log-entry">
          <b>${log.service}</b>: ${log.action}<br>
          ${new Date(log.timestamp * 1000).toLocaleTimeString()}
        </div>
      `).join("");
    })
    .catch(err => {
      const cont = document.getElementById("integration-logs");
      if (cont) cont.innerHTML = "<b>Error loading logs</b>";
    });
}

// ------- TEST INTEGRATIONS -------
function triggerAWSIsolation() {
  fetch(`${API}/integrations/aws/isolate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "isolate_sg",
      target: "sg-compromised-123",
      description: "Manual test"
    })
  })
    .then(res => res.json())
    .then(data => {
      alert("✅ AWS isolation triggered");
      loadIntegrationLogs();
    })
    .catch(err => alert("❌ AWS error: " + err));
}

function triggerOktaTokenRevoke() {
  fetch(`${API}/integrations/okta/revoke_token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "revoke_token",
      user_id: "compromised.user@company.com",
      reason: "Manual test"
    })
  })
    .then(res => res.json())
    .then(data => {
      alert("✅ Okta token revocation triggered");
      loadIntegrationLogs();
    })
    .catch(err => alert("❌ Okta error: " + err));
}

function triggerEDRQuarantine() {
  fetch(`${API}/integrations/edr/quarantine`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "quarantine_endpoint",
      endpoint_id: "endpoint-compromised-456",
      process_name: "malware.exe"
    })
  })
    .then(res => res.json())
    .then(data => {
      alert("✅ EDR quarantine triggered");
      loadIntegrationLogs();
    })
    .catch(err => alert("❌ EDR error: " + err));
}

// ------- EXPORT CSV -------
function exportCSV() {
  alert("✅ Export functionality coming soon!");
}

// ------- LOAD DASHBOARD -------
function loadDashboard() {
  loadAgents();
  loadEvents();
  loadIncidents();
  loadPolicy();
  loadPlaybooks();
  loadExecutionLogs();
  loadAIIncidents();
  loadIntegrationHealth();
  loadIntegrationLogs();
  
  setInterval(() => {
    loadAgents();
    loadEvents();
    loadIncidents();
    loadPlaybooks();
    loadExecutionLogs();
    loadAIIncidents();
    loadIntegrationHealth();
    loadIntegrationLogs();
  }, 15000);
}

// Auto-load on page init
loadPolicy();
// ------- ML DETECTION STATS -------
function loadMLStats() {
  fetch(`${API}/ml/stats`)
    .then(res => res.json())
    .then(stats => {
      const cont = document.getElementById("ml-stats");
      if (!cont) return;
      cont.innerHTML = `
        <b>🤖 ML Detection Status</b><br>
        Model: ${stats.model_status}<br>
        Events Analyzed: ${stats.total_events_analyzed}<br>
        Anomalies Found: ${stats.anomalies_detected}<br>
        Detection Rate: ${stats.detection_rate}%<br>
        Avg Anomaly Score: ${stats.avg_anomaly_score}
      `;
    });
}

// ------- SAAS ORG MANAGEMENT -------
function loadOrgBilling() {
  fetch(`${API}/saas/billing/${CURRENT_ORG}`)
    .then(res => res.json())
    .then(billing => {
      const cont = document.getElementById("org-billing");
      if (!cont) return;
      cont.innerHTML = `
        <b>${billing.org_name}</b><br>
        Tier: ${billing.subscription_tier} ($${billing.monthly_price}/mo)<br>
        Agents: ${billing.agents_used}/${billing.agents_limit}<br>
        Users: ${billing.users_used}/${billing.users_limit}<br>
        Status: ${billing.status}
      `;
    });
}

function getPlatformAnalytics() {
  fetch(`${API}/saas/analytics/platform`)
    .then(res => res.json())
    .then(analytics => {
      const cont = document.getElementById("platform-analytics");
      if (!cont) return;
      cont.innerHTML = `
        <b>📊 Platform Analytics</b><br>
        Organizations: ${analytics.total_organizations}<br>
        Total Users: ${analytics.total_users}<br>
        Monthly Revenue: $${analytics.monthly_recurring_revenue}<br>
        <b>Tier Breakdown:</b> ${JSON.stringify(analytics.tier_breakdown)}
      `;
    });
}

// Load on dashboard init
loadMLStats();
// ------- ML DETECTION STATS -------
function loadMLStats() {
  fetch(`${API}/ml/stats`)
    .then(res => res.json())
    .then(stats => {
      const cont = document.getElementById("ml-stats");
      if (!cont) return;
      cont.innerHTML = `
        <b>🤖 ML Detection Status</b><br>
        Model: ${stats.model_status}<br>
        Events Analyzed: ${stats.total_events_analyzed}<br>
        Anomalies Found: ${stats.anomalies_detected}<br>
        Detection Rate: ${stats.detection_rate}%<br>
        Avg Anomaly Score: ${stats.avg_anomaly_score}
      `;
    });
}

// ------- SAAS ORG MANAGEMENT -------
function loadOrgBilling() {
  fetch(`${API}/saas/billing/${CURRENT_ORG}`)
    .then(res => res.json())
    .then(billing => {
      const cont = document.getElementById("org-billing");
      if (!cont) return;
      cont.innerHTML = `
        <b>${billing.org_name}</b><br>
        Tier: ${billing.subscription_tier} ($${billing.monthly_price}/mo)<br>
        Agents: ${billing.agents_used}/${billing.agents_limit}<br>
        Users: ${billing.users_used}/${billing.users_limit}<br>
        Status: ${billing.status}
      `;
    });
}

function getPlatformAnalytics() {
  fetch(`${API}/saas/analytics/platform`)
    .then(res => res.json())
    .then(analytics => {
      const cont = document.getElementById("platform-analytics");
      if (!cont) return;
      cont.innerHTML = `
        <b>📊 Platform Analytics</b><br>
        Organizations: ${analytics.total_organizations}<br>
        Total Users: ${analytics.total_users}<br>
        Monthly Revenue: $${analytics.monthly_recurring_revenue}<br>
        <b>Tier Breakdown:</b> ${JSON.stringify(analytics.tier_breakdown)}
      `;
    });
}

// Load on dashboard init
loadMLStats();
loadOrgBilling();
getPlatformAnalytics