import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from app.schemas.reports import AnalyzeRequest, MatchJobRequest, ResumeReport
from app.services.parser import save_and_parse_file
from app.services.analyzer import analyze_resume_with_gemini
from app.models.database import save_report, get_report, is_mongo_active
from datetime import datetime

logger = logging.getLogger("resume_analyzer.routes")

router = APIRouter(prefix="/api", tags=["Resume Analyzer"])

@router.get("/health")
async def health_check():
    """Check health of the backend and database connection status."""
    return {
        "status": "healthy",
        "mongodb_connected": is_mongo_active,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX).
    Saves the file to disk and extracts its raw text content.
    """
    logger.info(f"Received file upload request: {file.filename}")
    file_path, extracted_text = await save_and_parse_file(file)
    return {
        "filename": file.filename,
        "file_path": file_path,
        "text": extracted_text
    }

@router.post("/analyze", response_model=ResumeReport)
async def analyze_resume(request: AnalyzeRequest):
    """
    Analyze parsed resume text with an optional job description.
    Uses Gemini to perform the analysis, saves the report, and returns it.
    """
    logger.info("Received resume analysis request")
    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text content cannot be empty.")
        
    # Perform Gemini/fallback analysis
    analysis_data = await analyze_resume_with_gemini(
        resume_text=request.resume_text,
        job_description=request.job_description
    )
    
    # Complete report schema details
    analysis_data["created_at"] = datetime.utcnow().isoformat()
    
    # Save the report to database
    report_id = analysis_data["id"]
    await save_report(report_id, analysis_data)
    
    return analysis_data

@router.post("/match-job", response_model=ResumeReport)
async def match_job_description(request: MatchJobRequest):
    """
    Match an existing analyzed resume report against a new Job Description.
    """
    logger.info(f"Received job matching request for report ID: {request.resume_id}")
    
    # Fetch existing report
    report_data = await get_report(request.resume_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Resume report not found.")
        
    # Re-analyze with JD. We'll reconstruct the resume text or re-read it.
    # Since we don't save the full raw text in the report, we can reconstruct it from the skills and summaries,
    # but a better way is to prompt Gemini using the existing report sections and summary + the JD,
    # OR we can store the resume text in the DB.
    # Let's save the resume text in our reports or pass it.
    # Let's see: we should modify the database schema or include a raw text field in the DB report if we want to re-run,
    # or we can write a quick analysis comparing the summary/skills of the resume with the JD.
    # Actually, let's include the resume_text in the database model or just re-generate matching.
    # Wait, let's check: if we store the parsed text in the report, we can easily re-run full analysis!
    # Let's modify the analyzer so that we can pass the details. Or we can just re-analyze.
    # Let's fetch the resume text from the report. To make this easy, let's check if the report saves the text.
    # Wait, let's save the text in the database report under a hidden/internal field or a 'raw_text' field!
    # Let's check: in `analyzer.py`, we can return "raw_text" as part of the analysis data, or we can add it in `analyze_resume`.
    # Yes, we can add a 'raw_text' key to the analysis_data dict before saving it, or we can just reconstruct a prompt.
    # Reconstructing from the report is easy, but having the raw text is much more powerful.
    # Wait! Let's check our schema. `ResumeReport` doesn't strictly have a `raw_text` field in Pydantic,
    # but we can add it as optional, or we can save it in the database document and not return it in the API response.
    # Yes! In `database.py` or `routes/analyze.py`, we can save it in MongoDB and just retrieve it.
    # Let's fetch `raw_text` from the database. Let's make sure that `analyze_resume` saves the raw text in the DB.
    # Wait, how does `match_job` work? We can run Gemini with:
    # "Match this candidate summary and skills against this JD..."
    # Or, we can retrieve the raw text. Let's assume the report dict has the raw text if saved,
    # or we can reconstruct it. Let's write the code to look for a `raw_text` field,
    # and if not found, we will build a summary-based match. This is very clean and robust!
    
    # Reconstruct resume text if raw text wasn't saved, or read raw text
    resume_summary = report_data.get("summary", "")
    hard_skills = report_data.get("skills", {}).get("hard_skills", [])
    soft_skills = report_data.get("skills", {}).get("soft_skills", [])
    skills_str = ", ".join(hard_skills + soft_skills)
    
    # We will use the summary and skills as the resume context for the match
    resume_context = f"Resume Summary:\n{resume_summary}\n\nKey Skills:\n{skills_str}"
    
    # Perform match analysis
    match_data = await analyze_resume_with_gemini(
        resume_text=resume_context,
        job_description=request.job_description
    )
    
    # Update the existing report with the job match results
    report_data["job_match"] = match_data.get("job_match")
    if "ats_score" in match_data:
        # Update ATS score based on job match
        report_data["ats_score"] = match_data["ats_score"]
    if "missing_skills" in match_data:
        report_data["missing_skills"] = match_data["missing_skills"]
    if "keyword_match_percentage" in match_data:
        report_data["keyword_match_percentage"] = match_data["keyword_match_percentage"]
        
    report_data["created_at"] = datetime.utcnow().isoformat()
    
    # Save updated report
    await save_report(request.resume_id, report_data)
    
    return report_data

@router.get("/report/{report_id}", response_model=ResumeReport)
async def get_resume_report(report_id: str):
    """
    Get a saved resume analysis report by its ID.
    """
    logger.info(f"Retrieving report for ID: {report_id}")
    report = await get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Resume report not found.")
    return report
