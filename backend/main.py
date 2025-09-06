


# import os, json, logging, requests
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# import pdfplumber
# from services.parser import parse_text



# # Load .env
# load_dotenv()
# NUTRIENT_API_KEY = os.getenv("NUTRIENT_API_KEY")

# # Folders
# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# app = FastAPI()

# # CORS fix
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5176", "*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# FILES = {}
# TABLES = {}

# def _safe_name(name: str) -> str:
#     return name.replace(" ", "_")

# # --- Upload Endpoint ---
# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     safe_name = _safe_name(file.filename)
#     save_path = os.path.join(UPLOAD_DIR, safe_name)

#     with open(save_path, "wb") as f:
#         f.write(await file.read())

#     FILES[safe_name] = {
#         "path": save_path,
#         "filename": safe_name,
#         "size": os.path.getsize(save_path),
#         "type": file.content_type,
#     }

#     return {
#         "filename": safe_name,
#         "size": os.path.getsize(save_path),
#         "type": file.content_type,
#     }


# @app.get("/")
# def root():
#     return {"message": "Backend is running!"}


# @app.get("/healthz")
# def health():
#     return {"status": "ok"}

# # --- Process Endpoint ---
# @app.post("/process/{filename}")
# def process_image(filename: str):
#     filename = _safe_name(filename)
#     if filename not in FILES:
#         raise HTTPException(status_code=404, detail=f"file {filename} not found")

#     if not NUTRIENT_API_KEY:
#         raise HTTPException(status_code=500, detail="Missing NUTRIENT_API_KEY in .env")

#     src_path = FILES[filename]["path"]

#     # Call Nutrient OCR API
#     with open(src_path, "rb") as f:
#         files = {"scanned": (filename, f, FILES[filename]["type"])}
#         payload = {
#             "instructions": json.dumps({
#                 "parts": [{"file": "scanned"}],
#                 "actions": [{"type": "ocr", "language": "english"}],
#             })
#         }
#         headers = {"Authorization": f"Bearer {NUTRIENT_API_KEY}"}

#         r = requests.post(
#             "https://api.nutrient.io/build",
#             headers=headers,
#             files=files,
#             data=payload,
#             stream=True,
#             timeout=120,
#         )

#     if not r.ok:
#         logging.error(f"Nutrient API error {r.status_code}: {r.text}")
#         raise HTTPException(status_code=502, detail=f"OCR service failed: {r.text}")

#     # Verify PDF response
#     if "application/pdf" not in r.headers.get("content-type", ""):
#         try:
#             err_preview = r.text[:300]
#         except Exception:
#             err_preview = "Non-PDF response"
#         raise HTTPException(status_code=500, detail=f"Unexpected response: {err_preview}")

#     # Save OCR PDF (temporary, only for parsing)
#     ocr_pdf_path = os.path.join(UPLOAD_DIR, f"{os.path.splitext(filename)[0]}_ocr.pdf")
#     with open(ocr_pdf_path, "wb") as out:
#         for chunk in r.iter_content(chunk_size=8192):
#             if chunk:
#                 out.write(chunk)

#     # Extract text
#     try:
#         text_chunks = []
#         with pdfplumber.open(ocr_pdf_path) as pdf:
#             for page in pdf.pages:
#                 text_chunks.append(page.extract_text() or "")
#         text = "\n".join(text_chunks)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to read OCR PDF: {e}")

#     # Parse into rows
#     rows_dicts = parse_text(text)
#     rows = [[r.get("date", ""), r.get("name", ""), r.get("check_in", ""), r.get("check_out", "")] for r in rows_dicts]

#     TABLES[filename] = rows
#     return {"rows": rows}





import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.ocr import extract_text_from_image, is_image
from services.parser import parse_text


# Folders
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Attendance OCR API (Local Only)")

# CORS fix for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://localhost:5176",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILES = {}
TABLES = {}

def _safe_name(name: str) -> str:
    """Sanitize file name to avoid spaces and unsafe characters."""
    return "".join(c for c in name if c.isalnum() or c in (" ", ".", "_", "-")).replace(" ", "_")


# --- Health Endpoints ---
@app.get("/")
def root():
    return {"message": "Backend is running locally (pytesseract OCR)"}

@app.get("/healthz")
def health():
    return {"status": "ok"}


# --- Upload Endpoint ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file name")

    safe_name = _safe_name(file.filename)
    save_path = os.path.join(UPLOAD_DIR, safe_name)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    with open(save_path, "wb") as f:
        f.write(content)

    FILES[safe_name] = {
        "path": save_path,
        "filename": safe_name,
        "size": os.path.getsize(save_path),
        "type": file.content_type,
    }

    return {
        "filename": safe_name,
        "size": os.path.getsize(save_path),
        "type": file.content_type,
    }


# --- Process Endpoint (Local OCR + Parser) ---
@app.post("/process/{filename}")
def process_image(filename: str):
    filename = _safe_name(filename)

    if filename not in FILES:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    src_path = FILES[filename]["path"]

    if not is_image(src_path):
        raise HTTPException(status_code=400, detail="File is not a supported image type")

    try:
        # ✅ Run local OCR
        text, _ = extract_text_from_image(src_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

    # ✅ Parse OCR text into structured rows
    rows_dicts = parse_text(text)
    rows = [
        [
            r.get("date", ""),
            r.get("name", ""),
            r.get("check_in", ""),
            r.get("check_out", ""),
        ]
        for r in rows_dicts
    ]

    # Store in memory (if needed later)
    TABLES[filename] = rows

    return {"rows": rows}
