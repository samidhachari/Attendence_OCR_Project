// import React from "react";

// export default function DataTable({ rows, setRows }) {
//   const updateCell = (idx, key, value) => {
//     const copy = [...rows];
//     copy[idx] = { ...copy[idx], [key]: value };
//     setRows(copy);
//   };

//   const addRow = () => setRows([...rows, { date: "", name: "", check_in: "", check_out: "" }]);
//   const removeRow = (idx) => setRows(rows.filter((_, i) => i !== idx));

//   if (!rows || rows.length === 0) {
//     return <p className="text-gray-500 mt-4">No data yet. Upload an image to extract attendance.</p>;
//   }

//   return (
//     <div className="mt-4">
//       <div className="overflow-x-auto border rounded-md bg-white">
//         <table className="min-w-full text-sm">
//           <thead className="bg-gray-100 text-left">
//             <tr>
//               <th className="p-3">Date (YYYY-MM-DD)</th>
//               <th className="p-3">Name</th>
//               <th className="p-3">Check In</th>
//               <th className="p-3">Check Out</th>
//               <th className="p-3"></th>
//             </tr>
//           </thead>
//           <tbody>
//             {rows.map((r, idx) => (
//               <tr key={idx} className="border-t">
//                 <td className="p-2">
//                   <input
//                     value={r.date}
//                     onChange={(e) => updateCell(idx, "date", e.target.value)}
//                     className="w-full border rounded px-2 py-1"
//                     placeholder="2025-08-01"
//                   />
//                 </td>
//                 <td className="p-2">
//                   <input
//                     value={r.name}
//                     onChange={(e) => updateCell(idx, "name", e.target.value)}
//                     className="w-full border rounded px-2 py-1"
//                     placeholder="Jane Doe"
//                   />
//                 </td>
//                 <td className="p-2">
//                   <input
//                     value={r.check_in}
//                     onChange={(e) => updateCell(idx, "check_in", e.target.value)}
//                     className="w-full border rounded px-2 py-1"
//                     placeholder="09:30"
//                   />
//                 </td>
//                 <td className="p-2">
//                   <input
//                     value={r.check_out}
//                     onChange={(e) => updateCell(idx, "check_out", e.target.value)}
//                     className="w-full border rounded px-2 py-1"
//                     placeholder="18:15"
//                   />
//                 </td>
//                 <td className="p-2 text-right">
//                   <button
//                     onClick={() => removeRow(idx)}
//                     className="px-2 py-1 text-red-600 hover:underline">
//                     Delete
//                   </button>
//                 </td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>
//       <button
//         onClick={addRow}
//         className="mt-3 px-3 py-2 rounded bg-gray-200 hover:bg-gray-300">
//         + Add Row
//       </button>
//     </div>
//   );
// }



import React, { useState } from "react";
import { saveAs } from "file-saver";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";


export default function DataTable({ tableData }) {
  const [rows, setRows] = useState(tableData || []);

  // Add row
  const addRow = () => {
    setRows([...rows, ["", "", "", ""]]);
  };

  // Delete row
  const deleteRow = (index) => {
    const updated = rows.filter((_, i) => i !== index);
    setRows(updated);
  };

  // Update cell
  const updateCell = (rowIndex, colIndex, value) => {
    const updated = [...rows];
    updated[rowIndex][colIndex] = value;
    setRows(updated);
  };

  // Export CSV
  const exportCSV = () => {
    const csv = rows.map(r => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    saveAs(blob, "table.csv");
  };

  // Export XLSX
  const exportXLSX = () => {
    const ws = XLSX.utils.aoa_to_sheet([["Date", "Name", "Check In", "Check Out"], ...rows]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
    XLSX.writeFile(wb, "table.xlsx");
  };

  // Export PDF
  const exportPDF = () => {
  try {
    const doc = new jsPDF();
    doc.text("Extracted Attendance Data", 14, 16);

    // Add serial numbers
    const rowsWithIndex = rows.map((r, i) => [i + 1, ...r]);

    // ✅ use autoTable() instead of doc.autoTable()
    autoTable(doc, {
      head: [["S.No.", "Date", "Name", "Check In", "Check Out"]],
      body: rowsWithIndex,
      startY: 20,
      styles: { fontSize: 10, cellPadding: 2 },
      headStyles: { fillColor: [41, 128, 185] },
    });

    doc.save("attendance_table.pdf");
  } catch (e) {
    console.error("PDF Export failed:", e);
    alert("Failed to export PDF");
  }
};






  return (
    <div className="w-full">
      <div className="overflow-y-auto max-h-96 border rounded-lg shadow-sm">
        <table className="w-full text-sm text-left border-collapse">
          <thead className="bg-gray-200 sticky top-0">
            <tr>
              <th className="p-2 border">S.No.</th>
              <th className="p-2 border">Date</th>
              <th className="p-2 border">Name</th>
              <th className="p-2 border">Check In</th>
              <th className="p-2 border">Check Out</th>
              <th className="p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {/* Serial No. column */}
                <td className="p-2 border text-center">{rowIndex + 1}</td>
                {row.map((cell, colIndex) => (
                  <td key={colIndex} className="p-2 border">
                    <input
                      type="text"
                      value={cell}
                      onChange={(e) => updateCell(rowIndex, colIndex, e.target.value)}
                      className="w-full border rounded px-2 py-1"
                    />
                  </td>
                ))}
                <td className="p-2 border text-center">
                  <button
                    onClick={() => deleteRow(rowIndex)}
                    className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-3 mt-4">
        <button
          onClick={addRow}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          + Add Row
        </button>

        <button
          onClick={exportCSV}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Export CSV
        </button>
        <button
          onClick={exportXLSX}
          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          Export XLSX
        </button>
        <button
          onClick={exportPDF}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
        Export PDF
        </button>
      </div>
    </div>
  );
}


