Attendance OCR Project

An end-to-end web application that automates attendance extraction from images and PDFs using OCR (Optical Character Recognition).
This project has two main components:
Backend (FastAPI + Tesseract OCR + Python) → Handles file uploads, OCR processing, and data export.
Frontend (React + Vite) → Provides a clean web UI for uploading documents and viewing attendance results.

The app is deployed on Render:
🌐 Frontend → https://attendence-ocr-frontend.onrender.com
⚙️ Backend API → https://attendence-ocr-project.onrender.com

Features
Upload images (JPG, PNG, JPEG) or PDF documents.
Extract attendance data using Tesseract OCR.
Display extracted attendance in a tabular format on the frontend.
Export results to Excel (XLSX) or PDF reports.
REST API built with FastAPI, interactive Swagger docs available.
Deployed on Render (backend + frontend) for production-ready hosting.

Tech Stack
Backend (in /backend/)
FastAPI → REST API framework
Uvicorn → ASGI server
Pytesseract → OCR engine (Tesseract wrapper)
Pillow → Image processing
Openpyxl → Export to Excel
ReportLab → Export to PDF
PdfPlumber → Extract text from PDFs
Python Dotenv → Env variable handling
Frontend (in /frontend/)
React 18 + Vite → Frontend framework + fast bundler
Axios → API communication
TailwindCSS → Styling
html2canvas → Capture/export frontend views

Deployment Render → Cloud hosting for both backend (web service) and frontend (static site)

Backend Setup (FastAPI)
# Clone repo
git clone https://github.com/samidhachari/Attendence_OCR_Project.git
cd Attendence_OCR_Project/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn main:app --reload


Backend will be live at: http://127.0.0.1:8000
Swagger Docs: http://127.0.0.1:8000/docs

Frontend Setup (React + Vite)
cd ../frontend
# Install dependencies
npm install
# Start dev server
npm run dev
Frontend will be live at: http://localhost:5173

Environment Variables
For connecting frontend → backend, set this in Render (Static Site → Environment Variables):
VITE_API_BASE=https://attendence-ocr-project.onrender.com

API Endpoints
Method	Endpoint	Description
GET	/healthz	Health check
POST	/upload/	Upload image/PDF for OCR
GET	/export/excel	Export extracted data (Excel)
GET	/export/pdf	Export extracted data (PDF)

Demo Flow
Open the frontend.
Upload an attendance sheet (image/PDF).
Backend extracts attendance using Tesseract OCR.
View results in table form.
Download as Excel/PDF report.

🚀 Deployment (Render)
Backend (Web Service)
Build Command → pip install -r requirements.txt
Start Command → uvicorn main:app --host 0.0.0.0 --port $PORT
Health Check Path → /healthz
Frontend (Static Site)
Build Command → npm install && npm run build
Publish Directory → frontend/dist
