from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PersonalInformation(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class SkillExtraction(BaseModel):
    hard_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)

class GrammarSuggestion(BaseModel):
    error: str = Field(..., description="The detected grammar or spelling error")
    suggestion: str = Field(..., description="Suggested correction")
    context: str = Field(..., description="Sentence context showing the error")

class SectionScore(BaseModel):
    section: str = Field(..., description="Section name, e.g., Experience, Education")
    score: int = Field(..., description="Score from 0 to 100")
    feedback: str = Field(..., description="Feedback for this specific section")

class JobMatchDetails(BaseModel):
    match_score: int = Field(..., description="ATS/Job Description match score from 0 to 100")
    keywords_matched: List[str] = Field(default_factory=list, description="Keywords from JD present in resume")
    keywords_missing: List[str] = Field(default_factory=list, description="Keywords from JD missing from resume")
    fit_feedback: str = Field(..., description="AI feedback on candidate's fit for this role")

class ResumeReport(BaseModel):
    id: str
    personal_info: PersonalInformation
    ats_score: int
    quality_score: int
    skills: SkillExtraction
    missing_skills: List[str] = Field(default_factory=list)
    keyword_match_percentage: int
    sections_analysis: List[SectionScore] = Field(default_factory=list)
    grammar_suggestions: List[GrammarSuggestion] = Field(default_factory=list)
    formatting_suggestions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    summary: str
    job_match: Optional[JobMatchDetails] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = None

class MatchJobRequest(BaseModel):
    resume_id: str
    job_description: str
