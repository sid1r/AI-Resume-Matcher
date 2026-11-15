
import re


SKILLS_LIST = [
    "python", "java", "javascript", "c", "c++",
    "sql", "mysql", "postgresql", "mongodb",
    "fastapi", "flask", "django", "react",
    "node.js", "rest api", "docker", "kubernetes",
    "aws", "azure", "git", "github",
    "machine learning", "deep learning",
    "nlp", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "html", "css"
]


def extract_email(text):
    match = re.search(
        r'[\w.+-]+@[\w-]+\.[\w.-]+',
        text
    )
    return match.group(0) if match else None


def extract_phone(text):
    match = re.search(
        r'(?<!\d)(?:\+?\d[\d\s().-]{8,16}\d)(?!\d)',
        text
    )
    return match.group(0).strip() if match else None


def extract_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if lines:
        first_line = lines[0]

        if "@" not in first_line and not re.search(r'\d', first_line):
            return first_line

    return None


def extract_skills(text):
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS_LIST:
        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills


def extract_experience(text):
    patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*years?'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return float(match.group(1))

    return None


def extract_education(text):
    education_keywords = [
        "b.tech", "b.e.", "bachelor",
        "b.sc", "bca", "m.tech",
        "mca", "master", "mba",
        "phd", "computer science"
    ]

    found = []

    for keyword in education_keywords:
        if keyword in text.lower():
            found.append(keyword)

    return list(dict.fromkeys(found))


def extract_candidate_info(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience_years": extract_experience(text),
        "education": extract_education(text)
    }
