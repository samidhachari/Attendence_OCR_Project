
import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import DataTable from "./components/DataTable";
import { uploadImage, processImage } from "./api";


export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileMeta, setFileMeta] = useState(null);
  const [rows, setRows] = useState([]);
  const [busy, setBusy] = useState(false);

  // Automatically upload when file selected
  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setBusy(true);
    try {
      const meta = await uploadImage(file);
      setFileMeta(meta);
      console.log("UPLOAD RESPONSE:", meta);
    } catch (e) {
      console.error(e);
      alert("Upload failed");
    } finally {
      setBusy(false);
    }
  };

  // Process image → extract table
  const handleProcess = async () => {
    if (!fileMeta?.filename) return alert("Upload an image first.");
    setBusy(true);
    try {
      const { rows } = await processImage(fileMeta.filename);
      setRows(rows || []);
      console.log("Processed:", rows);
    } catch (e) {
      console.error(e);
      alert("Processing failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-lg p-6 border">
        <h1 className="text-3xl font-bold text-blue-600 text-center mb-6">
          Image Data Extractor
        </h1>

        <div className="flex flex-col items-center gap-6">
            <FileUpload onUpload={handleFileSelect} />
            <button
              onClick={handleProcess}
              className="px-5 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-60"
              disabled={!fileMeta?.filename || busy}
            >
            {busy ? "Processing..." : "Process Image"}
            </button>         

          {selectedFile && (
            <div className="text-gray-700 bg-gray-50 p-4 rounded-lg shadow-sm w-full mt-4">
              <h2 className="text-lg font-semibold text-gray-800">File Details:</h2>
              <p><span className="font-medium">File Name:</span> {selectedFile.name}</p>
              <p><span className="font-medium">File Type:</span> {selectedFile.type}</p>
              <p><span className="font-medium">File Size:</span> {(selectedFile.size / 1024).toFixed(2)} KB</p>
            </div>
          )}
        </div>

        {rows.length > 0 && (
          <div className="mt-8 space-y-4">
            <h2 className="text-xl font-semibold">Extracted Table</h2>
            <DataTable tableData={rows} />
          </div>
        )}
      </div>
    </div>
  );
}







