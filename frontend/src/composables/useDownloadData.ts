export default function useDownloadData<T>(data: Ref<T[]>) {
  // Function to download the selected data as a CSV file
  function downloadData() {
    const dataToDownload = data.value;
    if (!dataToDownload || dataToDownload.length === 0) {
      console.warn("No data available for download.");
      return;
    }

    // Create CSV content from the data
    let csvContent = "Duration (s),Count\n";
    csvContent += dataToDownload.map((item) => `${item.duration},${item.count}`).join("\n");

    // Create a Blob from the CSV content and generate a URL
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "duration_histogram.csv";
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  return { downloadData };
}
