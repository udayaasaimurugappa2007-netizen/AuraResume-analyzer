# AuraResume | Premium AI Resume Analyzer & ATS Optimizer

AuraResume is a production-ready, full-stack resume scanning and scoring application designed with a dark, premium SaaS visual aesthetic (inspired by Linear, Vercel, and Notion AI). It parses uploaded resumes (PDF & DOCX), analyzes content using the Google Gemini API, computes ATS compatibility scores, extracts hard and soft skills, reviews grammar, layout formatting, and outputs customized improvement recommendations. Users can also enter target Job Descriptions for direct keyword-fit gap analysis.

## Features

- **Multi-Format Extraction**: Securely parse text from PDF (`pdfplumber`) and DOCX (`python-docx`) uploads.
- **Cognitive AI Auditing**: Analyzes layout hierarchy, action verbs, grammatical structures, and keyword metrics.
- **Circular Score Cards**: Interactive, color-coded SVG scoring rings representing ATS score and Resume Quality score.
- **Interactive Recharts Analysis**: Custom gradient-filled Area Chart mapping individual section scores (Experience, Projects, Education, etc.).
- **Missing Skill Gap Analysis**: Automatically highlights tool stack keywords present in the Job Description but missing from the resume.
- **Dynamic Job Matching**: Upload a job description on the fly to instantly run keyword comparisons and fit audits.
- **Print / PDF Download**: Clean printable media stylesheet to download formatted PDF reports of resume scans.
- **Intelligent Offline Fallback**: Switch seamlessly to local regex-based parsing and realistic mock analysis if the Gemini API key is missing.

---

## Tech Stack

### Frontend
- **React.js & Vite**: Fast development server and module bundler.
- **Tailwind CSS**: Utility-first CSS styling framework.
- **Framer Motion**: Smooth animations.
- **Recharts**: Data visualization charts.
- **React Dropzone**: Drag-and-drop file upload.
- **Axios**: Promised-based client for REST API communication.

### Backend
- **Python 3.7+ & FastAPI**: High-performance, type-safe API backend.
- **Uvicorn**: ASGI web server implementation.
- **Pydantic**: Data serialization and request body validation.
- **Google Generative AI**: Access to Google Gemini (`gemini-1.5-flash`).
- **MongoDB & Motor**: Asynchronous MongoDB client.

---

## Folder Structure

```text
resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── config.py           # Config variables & path definitions
│   │   ├── main.py             # FastAPI entry point & CORS configuration
│   │   ├── models/
│   │   │   └── database.py     # MongoDB client setup with local JSON fallback
│   │   ├── routes/
│   │   │   └── analyze.py      # /health, /upload, /analyze, /match-job, /report/{id}
│   │   ├── schemas/
│   │   │   └── reports.py      # Pydantic schemas for request/response validation
│   │   └── services/
│   │       ├── parser.py       # PDF & DOCX text extraction services
│   │       └── analyzer.py     # Gemini API integration & mock fallback
│   ├── uploads/                # Saved resumes
│   ├── reports/                # Mock DB reports output
│   ├── requirements.txt        # Python package dependencies
│   └── .env                    # Local environment config
├── frontend/
│   ├── src/
│   │   ├── components/         # Navbar, Footer, UploadBox, CircularScoreCard, SkillTags, Charts, Skeletons, Toast
│   │   ├── pages/              # LandingPage, UploadPage, DashboardPage
│   │   ├── services/
│   │   │   └── api.js          # Axios API communication Client
│   │   ├── index.css           # Glassmorphism, premium gradients, and custom animations
│   │   ├── App.jsx             # React routing setup
│   │   └── main.jsx            # Bootstrap entry point
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
└── README.md
```

---

## Installation & Running

Ensure you have **Node.js (v24+)** and **Python 3.7+** installed.

### 1. Setup the Backend

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   py -m venv venv
   # To activate on Windows:
   .\venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   py -m pip install -r requirements.txt
   ```

4. Configure your environment. Copy `.env.example` to `.env` and fill in your details:
   ```bash
   # Add your Google Gemini API Key
   GEMINI_API_KEY=your_google_gemini_api_key
   ```
   *Note: If no `GEMINI_API_KEY` is provided, the backend will automatically generate highly realistic mock resume reviews for local testing without crashing.*

5. Run the FastAPI server:
   ```bash
   py -m uvicorn app.main:app --reload --port 8000
   ```
   The backend documentation will be accessible at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Setup the Frontend

1. Open a new terminal window and navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to [http://localhost:5173](http://localhost:5173).
