const ctx = document.getElementById('statsChart').getContext('2d');
let statsChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Agents', 'Incidents', 'Blocked', 'Allowed'],
    datasets: [{
      label: "Live Security Stats",
      data: [0, 0, 0, 0],
      backgroundColor: ['#39FF14','#BC13FE','#f50087','#00F0FF']
    }]
  },
  options: { responsive: true, plugins: { legend: { labels: { color: '#39FF14'}}}}
});

async function updateChartData() {
 const agents = await fetch(`${API_BASE}/agent/`).then(r => r.json()).catch(() => []);
 const incidents = await fetch(`${API_BASE}/forensics/`).then(r => r.json()).catch(() => []);
 const policy = await fetch(`${API_BASE}/baseline/policy`).then(r => r.json()).catch(() => ({ allow: [], block: [] }));
  statsChart.data.datasets[0].data = [
    agents.length,
    incidents.length,
    policy.block.length,
    policy.allow.length
  ];
  statsChart.update();
}
setInterval(updateChartData, 5000);
updateChartData();
