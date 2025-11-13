// export.js
const API_BASE = "https://reflex-soc.onrender.com";

async function exportCSV() {
  try {
    // Fetch the export endpoint from your deployed backend
    const resp = await fetch(`${API_BASE}/forensics/export`);
    if (!resp.ok) {
      throw new Error("Export failed");
    }
    const blob = await resp.blob();

    // Create a download link for the CSV file
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

// You could add a button in your index.html like:
// <button onclick="exportCSV()">Export Incidents CSV</button>
