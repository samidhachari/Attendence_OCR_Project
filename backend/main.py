# import os
# import uuid
# from datetime import datetime
# from typing import List, Tuple

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, JSONResponse
# from pydantic import BaseModel
# import pandas as pd
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors

# from services.ocr import extract_text_from_image, is_image
# from services.parser import parse_text

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
# EXPORT_DIR = os.path.join(BASE_DIR, "exports")
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(EXPORT_DIR, exist_ok=True)

# app = FastAPI(title="Attendance OCR API")

# # Allow frontend to call (dev); change in production if needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class Record(BaseModel):
#     date: str
#     name: str
#     check_in: str
#     check_out: str

# class RecordsPayload(BaseModel):
#     records: List[Record]

# @app.get("/health")
# def health():
#     return {"ok": True, "time": datetime.utcnow().isoformat() + "Z"}

# def _safe_filename(name: str) -> str:
#     # very simple sanitizer
#     return "".join(c for c in name if c.isalnum() or c in (" ", ".", "_", "-")).strip()

# @app.post("/upload")
# async def upload(file: UploadFile = File(...)):
#     # read bytes (so we can capture size)
#     content = await file.read()
#     if not content:
#         raise HTTPException(status_code=400, detail="Empty file uploaded.")

#     original_name = file.filename or f"upload_{uuid.uuid4().hex}.png"
#     safe_name = f"{uuid.uuid4().hex}_{_safe_filename(original_name)}"
#     dst_path = os.path.join(UPLOAD_DIR, safe_name)

#     # Save file
#     with open(dst_path, "wb") as f:
#         f.write(content)

#     # Basic metadata to return
#     file_meta = {
#         "original_name": original_name,
#         "saved_name": safe_name,
#         "size_kb": round(len(content) / 1024, 1),
#         "content_type": file.content_type or "unknown"
#     }

#     # check extension
#     if not is_image(original_name):
#         # still allow but warn
#         return JSONResponse(status_code=400, content={"ok": False, "detail": "Only images supported (png/jpg/jpeg/webp/tiff).", "file_meta": file_meta})

#     try:
#         text, _ = extract_text_from_image(dst_path)
#     except Exception as e:
#         # OCR failed
#         return JSONResponse(status_code=500, content={"ok": False, "detail": f"OCR failed: {str(e)}", "file_meta": file_meta})

#     parsed = parse_text(text)

#     return {"ok": True, "file_meta": file_meta, "text": text, "data": parsed}

# @app.post("/export/excel")
# def export_excel(payload: RecordsPayload):
#     if not payload.records or len(payload.records) == 0:
#         raise HTTPException(status_code=400, detail="No records to export.")

#     # Use pydantic v2 model_dump to convert to dicts
#     rows = [r.model_dump() for r in payload.records]
#     df = pd.DataFrame(rows)
#     df = df[["date", "name", "check_in", "check_out"]]

#     stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     fname = f"attendance_{stamp}.xlsx"
#     path = os.path.join(EXPORT_DIR, fname)
#     df.to_excel(path, index=False)
#     return {"ok": True, "filename": fname, "url": f"/download/{fname}"}

# def _draw_table_pdf(c: canvas.Canvas, data, x, y, col_widths):
#     row_height = 20
#     for row_idx, row in enumerate(data):
#         cy = y - row_idx * row_height
#         cx = x
#         for col_idx, cell in enumerate(row):
#             width = col_widths[col_idx]
#             c.rect(cx, cy - row_height, width, row_height, stroke=1, fill=0)
#             c.drawString(cx + 4, cy - row_height + 6, str(cell)[:60])
#             cx += width

# @app.post("/export/pdf")
# def export_pdf(payload: RecordsPayload):
#     if not payload.records or len(payload.records) == 0:
#         raise HTTPException(status_code=400, detail="No records to export.")

#     stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     fname = f"attendance_{stamp}.pdf"
#     path = os.path.join(EXPORT_DIR, fname)

#     c = canvas.Canvas(path, pagesize=A4)
#     width, height = A4

#     title = "Attendance Report"
#     c.setFont("Helvetica-Bold", 16)
#     c.drawString(40, height - 50, title)
#     c.setFont("Helvetica", 10)
#     c.setFillColor(colors.gray)
#     c.drawString(40, height - 65, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     c.setFillColor(colors.black)

#     header = ["Date", "Name", "Check In", "Check Out"]
#     rows = [header] + [[r.date, r.name, r.check_in, r.check_out] for r in payload.records]
#     col_widths = [120, 220, 100, 100]

#     start_x = 40
#     start_y = height - 100
#     _draw_table_pdf(c, rows, start_x, start_y, col_widths)

#     c.showPage()
#     c.save()

#     return {"ok": True, "filename": fname, "url": f"/download/{fname}"}

# @app.get("/download/{filename}")
# def download(filename: str):
#     path = os.path.join(EXPORT_DIR, filename)
#     if not os.path.exists(path):
#         raise HTTPException(status_code=404, detail="File not found")
#     media_type = "application/octet-stream"
#     if filename.lower().endswith(".xlsx"):
#         media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     if filename.lower().endswith(".pdf"):
#         media_type = "application/pdf"
#     return FileResponse(path, media_type=media_type, filename=filename)





# import os, json, logging, requests
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from dotenv import load_dotenv
# import pdfplumber
# from services.parser import parse_text
# from fastapi.responses import FileResponse
# import tempfile

 
# #Load .env
# load_dotenv()
# NUTRIENT_API_KEY = os.getenv("NUTRIENT_API_KEY")

# #Folders
# UPLOAD_DIR = "uploads"
# EXPORT_DIR = "exports"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(EXPORT_DIR, exist_ok=True)

# app = FastAPI()

# #CORS fix
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173","http://localhost:5174", "http://localhost:5176", "*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# FILES = {}
# TABLES = {}

# def _safe_name(name: str) -> str:
#     return name.replace(" ", "_")

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

# @app.post("/process/{filename}")
# def process_image(filename: str):
#     filename = _safe_name(filename)
#     if filename not in FILES:
#         raise HTTPException(status_code=404, detail=f"file {filename} not found")

#     if not NUTRIENT_API_KEY:
#         raise HTTPException(status_code=500, detail="Missing NUTRIENT_API_KEY in .env")

#     src_path = FILES[filename]["path"]

#     # Call Nutrient API
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

#     #Verify PDF response
#     if "application/pdf" not in r.headers.get("content-type", ""):
#         try:
#             err_preview = r.text[:300]
#         except Exception:
#             err_preview = "Non-PDF response"
#         raise HTTPException(status_code=500, detail=f"Unexpected response: {err_preview}")

#     #Save OCR PDF
#     ocr_pdf_path = os.path.join(EXPORT_DIR, f"{os.path.splitext(filename)[0]}_ocr.pdf")
#     with open(ocr_pdf_path, "wb") as out:
#         for chunk in r.iter_content(chunk_size=8192):
#             if chunk:
#                 out.write(chunk)

#     #Extract text
#     try:
#         text_chunks = []
#         with pdfplumber.open(ocr_pdf_path) as pdf:
#             for page in pdf.pages:
#                 text_chunks.append(page.extract_text() or "")
#         text = "\n".join(text_chunks)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to read OCR PDF: {e}")

#     #Parse
#     rows_dicts = parse_text(text)
#     rows = [[r.get("date", ""), r.get("name", ""), r.get("check_in", ""), r.get("check_out", "")] for r in rows_dicts]

#     TABLES[filename] = rows
#     return {"rows": rows}





import os, json, logging, requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import pdfplumber
from services.parser import parse_text

# Load .env
load_dotenv()
NUTRIENT_API_KEY = os.getenv("NUTRIENT_API_KEY")

# Folders
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# CORS fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5176", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILES = {}
TABLES = {}

def _safe_name(name: str) -> str:
    return name.replace(" ", "_")

# --- Upload Endpoint ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    safe_name = _safe_name(file.filename)
    save_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(save_path, "wb") as f:
        f.write(await file.read())

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

# --- Process Endpoint ---
@app.post("/process/{filename}")
def process_image(filename: str):
    filename = _safe_name(filename)
    if filename not in FILES:
        raise HTTPException(status_code=404, detail=f"file {filename} not found")

    if not NUTRIENT_API_KEY:
        raise HTTPException(status_code=500, detail="Missing NUTRIENT_API_KEY in .env")

    src_path = FILES[filename]["path"]

    # Call Nutrient OCR API
    with open(src_path, "rb") as f:
        files = {"scanned": (filename, f, FILES[filename]["type"])}
        payload = {
            "instructions": json.dumps({
                "parts": [{"file": "scanned"}],
                "actions": [{"type": "ocr", "language": "english"}],
            })
        }
        headers = {"Authorization": f"Bearer {NUTRIENT_API_KEY}"}

        r = requests.post(
            "https://api.nutrient.io/build",
            headers=headers,
            files=files,
            data=payload,
            stream=True,
            timeout=120,
        )

    if not r.ok:
        logging.error(f"Nutrient API error {r.status_code}: {r.text}")
        raise HTTPException(status_code=502, detail=f"OCR service failed: {r.text}")

    # Verify PDF response
    if "application/pdf" not in r.headers.get("content-type", ""):
        try:
            err_preview = r.text[:300]
        except Exception:
            err_preview = "Non-PDF response"
        raise HTTPException(status_code=500, detail=f"Unexpected response: {err_preview}")

    # Save OCR PDF (temporary, only for parsing)
    ocr_pdf_path = os.path.join(UPLOAD_DIR, f"{os.path.splitext(filename)[0]}_ocr.pdf")
    with open(ocr_pdf_path, "wb") as out:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                out.write(chunk)

    # Extract text
    try:
        text_chunks = []
        with pdfplumber.open(ocr_pdf_path) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
        text = "\n".join(text_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read OCR PDF: {e}")

    # Parse into rows
    rows_dicts = parse_text(text)
    rows = [[r.get("date", ""), r.get("name", ""), r.get("check_in", ""), r.get("check_out", "")] for r in rows_dicts]

    TABLES[filename] = rows
    return {"rows": rows}
