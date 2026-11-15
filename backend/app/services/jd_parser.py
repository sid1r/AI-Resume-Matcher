
import re

from app.services.candidate_extractor import SKILLS_LIST


def extract_jd_skills(jd_text: str):
    """Identify required skills mentioned in a job description."""

    text = jd_text.lower()
    found_skills = []

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills



def extract_jd_experience(jd_text: str):
    """Extract required years of experience."""

    patterns = [
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*years?",
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience",
        r"minimum\s+(\d+(?:\.\d+)?)\+?\s*years?",
        r"at least\s+(\d+(?:\.\d+)?)\s+years?"
    ]

    for pattern in patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)

        if match:
            return float(match.group(1))

    return None



def extract_jd_qualifications(jd_text: str):
    """Identify educational qualifications."""

    keywords = [
        "b.tech",
        "b.e.",
        "bachelor",
        "b.sc",
        "bca",
        "m.tech",
        "mca",
        "master",
        "mba",
        "phd",
        "computer science",
        "information technology"
    ]

    text = jd_text.lower()

    return [
        keyword for keyword in keywords
        if keyword in text
    ]


def analyze_job_description(jd_text: str):
    """Extract important job requirements."""

    if not jd_text or not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    return {
        "required_skills": extract_jd_skills(jd_text),
        "required_experience_years": extract_jd_experience(jd_text),
        "required_qualifications": extract_jd_qualifications(jd_text)
    }
