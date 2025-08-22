
// import axios from "axios";

// const API = axios.create({
//   baseURL: "http://localhost:8000",
//   timeout: 30000,
// });

// export const uploadImage = async (file) => {
//   const form = new FormData();
//   form.append("file", file);
//   const { data } = await API.post("/upload", form, {
//     headers: { "Content-Type": "multipart/form-data" },
//   });
//   return data; // { filename, size, type }
// };

// export const processImage = async (filename) => {
//   const { data } = await API.post(`/process/${encodeURIComponent(filename)}`);
//   return data; // { rows }
// };

// export default API;


import axios from "axios";

// Use env var if available, else default to local
// const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const API_BASE = "https://attendence-ocr-project.onrender.com";

const API = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const uploadImage = async (file) => {
  const form = new FormData();
  form.append("file", file);
  const { data } = await API.post("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data; // { filename, size, type }
};

export const processImage = async (filename) => {
  const { data } = await API.post(`/process/${encodeURIComponent(filename)}`);
  return data; // { rows }
};

export default API;


