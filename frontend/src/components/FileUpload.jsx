import React, { useRef } from "react";

export default function FileUpload({ onUpload }) {
  const inputRef = useRef(null);

  const onFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    onUpload(file);
    e.target.value = "";
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={() => inputRef.current?.click()}
        className="px-4 py-2 rounded-md bg-indigo-600 text-white hover:bg-indigo-700">
        Upload Image
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onFileChange}
      />
      <p className="text-sm text-gray-500">
        PNG / JPG / JPEG / WEBP / TIFF
      </p>
    </div>
  );
}



