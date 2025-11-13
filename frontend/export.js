async function exportCSV() {
  // Fetch the export endpoint
  const resp = await fetch("http://localhost:8899/forensics/export");

  // Detect CSV response type, fallback to JSON otherwise
  const contentType = resp.headers.get("Content-Type") || "";
  if (contentType.includes("text/csv")) {
    // Handle as CSV (download file)
    const csv = await resp.text();
    const blob = new Blob([csv], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "evidence.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    return;
  }

  // Else, treat as JSON and build CSV as before
  const evidence = await resp.json();
  let csv = "id,action,score,timestamp\n";
  for (const e of evidence) {
    csv += `${e.id},"${e.action}",${e.details?.score || ""},${e.created_at}\n`;
  }
  const blob = new Blob([csv], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "evidence.csv";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
