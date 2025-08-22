// import React, { useState } from "react";
// import FileUpload from "./components/FileUpload.jsx";
// import DataTable from "./components/DataTable.jsx";
// import ExportButtons from "./components/ExportButtons.jsx";
// import { uploadImage } from "./api.js";


// export default function App() {
//   const [rows, setRows] = useState([]);
//   const [rawText, setRawText] = useState("");
//   const [fileMeta, setFileMeta] = useState(null);
//   const [savedName, setSavedName] = useState("");


//   const handleUpload = async (file) => {
//     setFileMeta({
//       original_name: file.name,
//       size_kb: (file.size / 1024).toFixed(1) + " KB",
//       type: file.type || "unknown"
//     });



//     try {
//       const res = await uploadImage(file);
//       if (!res.ok) {
//         alert("Upload error: " + (res.detail || "see console"));
//         console.error(res);
//         return;
//       }

//       setSavedName(res.file_meta?.saved_name || "");
//       setRawText(res.text || "");
//       setRows(res.data || []);
//     } catch (e) {
//       alert("Upload failed. Check backend is running and CORS. See console for details.");
//       console.error(e);
//     }
//   };

//   return (
//     <div className="max-w-5xl mx-auto p-4">
//       <h1 className="text-2xl font-semibold">Attendance OCR</h1>
//       <p className="text-gray-600">Upload an attendance image → auto-extract → edit → export.</p>

//       <div className="mt-4">
//         <FileUpload onUpload={handleUpload} />
//       </div>

//       {fileMeta && (
//         <div className="mt-3 text-sm text-gray-500">
//           <div><strong>Original:</strong> {fileMeta.original_name}</div>
//           <div><strong>Size:</strong> {fileMeta.size_kb}</div>
//           <div><strong>Type:</strong> {fileMeta.type}</div>
//           {savedName && <div><strong>Saved as:</strong> {savedName}</div>}
//         </div>
//       )}

//       <DataTable rows={rows} setRows={setRows} />

//       <ExportButtons rows={rows} />

//       <details className="mt-6">
//         <summary className="cursor-pointer text-sm text-gray-700">Show raw OCR text</summary>
//         <pre className="mt-2 p-3 bg-white border rounded whitespace-pre-wrap text-xs">{rawText}</pre>
//       </details>

//       <footer class="mt-10 py-6 text-center text-gray-500 text-sm">
//         © 2025 Task 2
//       </footer>
//     </div>
//   );
// }



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

        <div className="flex flex-col items-center gap-4">
          {/* Upload component now triggers auto-upload */}
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
              {/* {fileMeta?.filename && (
                <p className="text-sm text-green-700 mt-1">Uploaded as: {fileMeta.filename}</p>
              )} */}
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





