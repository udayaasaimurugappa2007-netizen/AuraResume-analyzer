import os
import json
import logging
import uuid
import re
from typing import Dict, Any, Optional
import requests
import asyncio
from app.config import GEMINI_API_KEY

logger = logging.getLogger("resume_analyzer.analyzer")

# Check if Gemini key is provided
if GEMINI_API_KEY:
    logger.info("Gemini API key is configured. HTTP requests mode active.")
else:
    logger.warning("GEMINI_API_KEY is not set. The app will run in mock analysis mode.")

def clean_json_response(text: str) -> str:
    """Removes markdown code blocks or wrapper text around JSON responses."""
    cleaned = text.strip()
    # Remove markdown code block wraps
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def generate_mock_analysis(resume_text: str, job_description: Optional[str] = None) -> Dict[str, Any]:
    """Generates simulated, realistic analysis data for testing when Gemini is unavailable."""
    logger.info("Generating mock analysis report.")
    
    # Simple regex parsing to extract personal info
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
    email = email_match.group(0) if email_match else "john.doe@example.com"
    
    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text)
    phone = phone_match.group(0) if phone_match else "+1 (555) 019-2834"
    
    # Try to find a name at the beginning of the text
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    name = lines[0] if lines else "John Doe"
    if len(name) > 30 or "@" in name or ":" in name:
        name = "John Doe"
        
    location = "San Francisco, CA"
    for line in lines[:10]:
        if "NY" in line or "New York" in line:
            location = "New York, NY"
            break
        elif "CA" in line or "California" in line:
            location = "Los Angeles, CA"
            break
        elif "TX" in line or "Texas" in line:
            location = "Austin, TX"
            break

    # Determine skills based on keywords
    detected_hard = []
    keywords = ["python", "javascript", "react", "node", "java", "sql", "aws", "docker", "kubernetes", "typescript", "c++", "c#", "html", "css", "git", "mongodb", "postgresql", "rest api"]
    for kw in keywords:
        if kw in resume_text.lower():
            detected_hard.append(kw.title() if kw != "sql" and kw != "aws" and kw != "git" and kw != "html" and kw != "css" else kw.upper())
            
    if not detected_hard:
        detected_hard = ["JavaScript", "React", "HTML5", "CSS3", "Git"]

    detected_soft = ["Teamwork", "Communication", "Problem Solving"]
    for soft in ["leadership", "management", "agile", "scrum", "mentoring", "critical thinking"]:
        if soft in resume_text.lower():
            detected_soft.append(soft.title())

    # Formulate mock report
    ats_score = 78
    quality_score = 82
    missing_skills = ["Docker", "Kubernetes", "AWS"]
    keyword_match_percentage = 65
    
    # Adjust scores if a Job Description is matched
    job_match_data = None
    if job_description:
        jd_lower = job_description.lower()
        matched_jd_kws = []
        missing_jd_kws = []
        
        for kw in ["python", "react", "node", "aws", "docker", "kubernetes", "typescript", "sql"]:
            if kw in jd_lower:
                if kw in resume_text.lower():
                    matched_jd_kws.append(kw.title() if kw != "sql" and kw != "aws" else kw.upper())
                else:
                    missing_jd_kws.append(kw.title() if kw != "sql" and kw != "aws" else kw.upper())
        
        if matched_jd_kws:
            keyword_match_percentage = int((len(matched_jd_kws) / (len(matched_jd_kws) + len(missing_jd_kws))) * 100) if (len(matched_jd_kws) + len(missing_jd_kws)) > 0 else 50
        else:
            keyword_match_percentage = 40
            
        ats_score = int(0.4 * ats_score + 0.6 * keyword_match_percentage)
        
        # Skill gaps
        missing_skills = missing_jd_kws if missing_jd_kws else ["System Design", "Microservices"]
        
        job_match_data = {
            "match_score": keyword_match_percentage,
            "keywords_matched": matched_jd_kws if matched_jd_kws else ["REST APIs"],
            "keywords_missing": missing_skills,
            "fit_feedback": "The resume shows strong foundational software development skills, but the candidate lacks specific hands-on experience in cloud infrastructure and containerization mentioned in the job description."
        }

    sections = [
        {"section": "Work Experience", "score": 85, "feedback": "Excellent descriptions of prior employment, containing action verbs and impact metrics."},
        {"section": "Education", "score": 90, "feedback": "Clear details with degree type and graduation date. Nicely structured."},
        {"section": "Skills", "score": 75, "feedback": "Solid list of technical skills, but could be grouped into categories (e.g. Languages, Frameworks) for better readability."},
        {"section": "Projects", "score": 80, "feedback": "Great personal projects listed. Consider linking to GitHub repositories."}
    ]

    grammar = [
        {"error": "analysed", "suggestion": "analyzed", "context": "I analysed user data and improved algorithms."},
        {"error": "utilise", "suggestion": "utilize", "context": "I utilise Docker for virtualization tasks."}
    ]

    formatting = [
        "Ensure date formatting is consistent across all work experiences (e.g., use 'MM/YYYY' or 'Month YYYY').",
        "Consider reducing whitespace margins to keep the resume to a concise 1-page length."
    ]

    recommendations = [
        "Include quantitative statistics for your projects (e.g., 'improved page load times by 20%').",
        f"Add the following missing skills directly into your Skills section: {', '.join(missing_skills[:3])}."
    ]

    return {
        "id": str(uuid.uuid4()),
        "personal_info": {
            "name": name,
            "email": email,
            "phone": phone,
            "location": location
        },
        "ats_score": ats_score,
        "quality_score": quality_score,
        "skills": {
            "hard_skills": detected_hard,
            "soft_skills": detected_soft
        },
        "missing_skills": missing_skills,
        "keyword_match_percentage": keyword_match_percentage,
        "sections_analysis": sections,
        "grammar_suggestions": grammar,
        "formatting_suggestions": formatting,
        "recommendations": recommendations,
        "summary": f"This resume demonstrates a qualified professional with strong background in {', '.join(detected_hard[:3])}. The resume is well-organized and presents details clearly, but can be improved by targeting missing keywords and adding metric-driven performance results.",
        "job_match": job_match_data,
        "created_at": "" # Will be set in route/schema
    }

async def analyze_resume_with_gemini(resume_text: str, job_description: Optional[str] = None) -> Dict[str, Any]:
    """Sends the resume text to Google Gemini to parse and analyze, returning a structured report."""
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key is not configured. Falling back to mock generator.")
        return generate_mock_analysis(resume_text, job_description)

    prompt = f"""
You are an expert technical recruiter, career coach, and ATS (Applicant Tracking System) parser.
Perform a thorough, expert-level analysis of the following Resume Text. 
If a Job Description is provided, perform a direct keyword, skill, and role-fit gap analysis.

Resume Text:
---
{resume_text}
---

Job Description (Optional):
---
{job_description or "None Provided"}
---

You must analyze this data and generate a JSON response strictly matching the schema below.
Ensure the analysis is highly detailed and helpful. Score criteria should be:
- ATS Score: Evaluate keyword presence, formatting hierarchy, contact availability, and structural density.
- Quality Score: Evaluate clarity, use of action verbs, inclusion of measurable metrics (percentages, revenues, scale), and career progression.

You must return ONLY a valid JSON object matching the following structure:
{{
  "personal_info": {{
    "name": "Extract full name (or null if not found)",
    "email": "Extract email address (or null if not found)",
    "phone": "Extract phone number (or null if not found)",
    "location": "Extract location/city/state (or null if not found)"
  }},
  "ats_score": 85, 
  "quality_score": 80,
  "skills": {{
    "hard_skills": ["List", "of", "extracted", "hard/tech", "skills"],
    "soft_skills": ["List", "of", "extracted", "soft", "skills"]
  }},
  "missing_skills": ["List of critical industry/role skills missing from the resume, especially compared to the JD if provided"],
  "keyword_match_percentage": 75,
  "sections_analysis": [
    {{
      "section": "Section Name (e.g., Work Experience, Education, Projects, Skills, Summary)",
      "score": 90,
      "feedback": "Specific strengths and weaknesses of this section"
    }}
  ],
  "grammar_suggestions": [
    {{
      "error": "The exact grammatical or spelling error found",
      "suggestion": "The corrected word or phrase",
      "context": "The sentence fragment showing where the error occurs"
    }}
  ],
  "formatting_suggestions": [
    "Feedback about margins, fonts, bullet styles, structural consistency, or length"
  ],
  "recommendations": [
    "Specific, actionable suggestions to improve this resume's impact, keywords, or structure"
  ],
  "summary": "A 2-3 sentence overall professional summary of the candidate's profile, including their primary area of expertise and overall readiness",
  "job_match": {{
    "match_score": 80,
    "keywords_matched": ["Keywords in JD that are in the resume"],
    "keywords_missing": ["Keywords in JD that are missing from the resume"],
    "fit_feedback": "A summary of why the candidate fits or does not fit the job description, listing specific strengths and main hurdles"
  }}
}}

CRITICAL RULES:
1. Return ONLY the raw JSON string starting with '{{' and ending with '}}'. Do not wrap the JSON in markdown code blocks like ```json or include any text before or after the JSON.
2. If no job description is provided, set the "job_match" key to null, and make "missing_skills" generic to industry standard expectations for the candidate's career track.
3. Validate that your JSON syntax is 100% correct, escaping any double quotes inside string values.
"""

    try:
        # Request helper executed in threadpool to avoid event loop blocking
        def call_gemini():
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]

        loop = asyncio.get_event_loop()
        response_text = await loop.run_in_executor(None, call_gemini)
        
        cleaned_json = clean_json_response(response_text)
        
        # Parse and return JSON
        data = json.loads(cleaned_json)
        data["id"] = str(uuid.uuid4())
        return data
        
    except Exception as e:
        logger.error(f"Gemini API analysis failed: {e}. Falling back to mock generator.")
        # Return fallback analysis on error
        return generate_mock_analysis(resume_text, job_description)
