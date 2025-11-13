const API_BASE = "https://reflex-soc.onrender.com";

async function exportCSV() {
  try {
    const resp = await fetch(`${API_BASE}/forensics/export`);
    if (!resp.ok) throw new Error("Export failed");
    const blob = await resp.blob();

    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "incidents_export.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (err) {
    alert("Failed to export: " + err.message);
  }
}
