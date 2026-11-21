import re
from datetime import datetime
from typing import Any


# --------------------------------------------------
# KEYWORD LISTS
# --------------------------------------------------

SKILLS_LIST = [
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle",
    "fastapi", "flask", "django", "react", "node.js", "express",
    "html", "css", "rest api", "git", "github", "docker", "kubernetes",
    "aws", "azure", "linux", "machine learning", "deep learning",
    "natural language processing", "nlp", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "opencv",
    "computer vision", "generative ai", "langchain", "chromadb",
    "power bi", "tableau", "jenkins", "redis", "spring boot",
]

FUNCTIONAL_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving",
    "problem-solving", "project management", "time management",
    "critical thinking", "analytical skills", "decision making",
    "adaptability", "collaboration", "client management",
    "presentation skills", "interpersonal skills", "conflict resolution",
    "attention to detail", "multitasking",
]

SECTION_HEADINGS = {
    "summary", "professional summary", "career objective", "objective",
    "work experience", "professional experience", "experience",
    "employment history", "internships", "internship experience",
    "education", "academic background", "technical skills", "skills",
    "functional skills", "projects", "personal projects",
    "certifications", "certificates", "achievements", "languages",
    "personal details", "publications", "positions of responsibility",
    "previous companies",
}


# --------------------------------------------------
# COMMON HELPERS
# --------------------------------------------------

def _normalise_heading(line: str) -> str:
    line = re.sub(r"^\s*[\#\-\*•]+\s*", "", line or "")
    line = re.sub(r"[\*_`]", "", line)
    line = re.sub(r"[\s:：\-]+$", "", line)
    return re.sub(r"\s+", " ", line).strip().lower()


def _is_section_heading(line: str) -> bool:
    return _normalise_heading(line) in SECTION_HEADINGS


def extract_section(text: str, section_name: str) -> list[str]:
    """Extract lines under a section until the next recognized heading."""

    if not text:
        return []

    target = _normalise_heading(section_name)
    collecting = False
    output = []

    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        line = raw_line.strip()

        if not line:
            if collecting and output and output[-1] != "":
                output.append("")
            continue

        heading = _normalise_heading(line)

        if heading == target:
            collecting = True
            continue

        if collecting and heading in SECTION_HEADINGS:
            break

        if collecting:
            output.append(line)

    while output and not output[-1]:
        output.pop()

    return output


def find_keywords(text: str, keywords: list[str]) -> list[str]:
    """Find keywords in text without case sensitivity."""

    text = text or ""
    found = []

    for keyword in keywords:
        pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found.append(keyword)

    return found


# --------------------------------------------------
# CONTACT INFORMATION
# --------------------------------------------------

def extract_email(text: str) -> str | None:
    """Extract email address."""

    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text or "",
    )

    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Extract a phone number containing 10-15 digits."""

    if not text:
        return None

    candidates = re.findall(
        r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)",
        text,
    )

    for candidate in candidates:
        digits = re.sub(r"\D", "", candidate)

        if 10 <= len(digits) <= 15:
            return candidate.strip()

    return None


def extract_name(text: str) -> str | None:
    """Extract a likely candidate name from the first few lines."""

    if not text:
        return None

    ignored = (
        "resume", "curriculum vitae", "phone", "email", "linkedin",
        "github", "portfolio", "address", "profile",
    )

    for raw_line in text.splitlines()[:12]:
        line = raw_line.strip(" \t|,-")

        if not line or "@" in line or re.search(r"\d", line):
            continue

        if any(word in line.lower() for word in ignored):
            continue

        if _is_section_heading(line):
            continue

        if len(line) <= 60 and 1 < len(line.split()) <= 5:
            return line

    return None


# --------------------------------------------------
# TECHNICAL AND FUNCTIONAL SKILLS
# --------------------------------------------------

def extract_skills(text: str) -> list[str]:
    """Extract technical skills."""

    return find_keywords(text, SKILLS_LIST)


def extract_functional_skills(text: str) -> list[str]:
    """Extract functional skills."""

    found = find_keywords(text, FUNCTIONAL_SKILLS)

    if "problem-solving" in found:
        found.remove("problem-solving")

        if "problem solving" not in found:
            found.append("problem solving")

    return found


# --------------------------------------------------
# EXPERIENCE
# --------------------------------------------------

def get_work_experience_text(text: str) -> str:
    """Extract work experience and internship sections."""

    headings = [
        "WORK EXPERIENCE",
        "PROFESSIONAL EXPERIENCE",
        "EXPERIENCE",
        "EMPLOYMENT HISTORY",
        "INTERNSHIPS",
        "INTERNSHIP EXPERIENCE",
    ]

    sections = []

    for heading in headings:
        section = extract_section(text or "", heading)

        if section:
            sections.extend(section)

    return "\n".join(sections).strip()


def extract_experience(text: str) -> float:
    """Extract explicit experience or estimate from date ranges."""

    if not text:
        return 0.0

    explicit_patterns = [
        r"(?:total\s+)?(?:professional\s+)?experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience",
    ]

    for pattern in explicit_patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return float(match.group(1))

    experience_text = get_work_experience_text(text) or text

    now = datetime.now()
    total_months = 0

    month_pattern = (
        r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    )

    date_patterns = [
        re.compile(
            rf"\b{month_pattern}\s+(\d{{4}})\s*(?:-|–|—|to)\s*"
            rf"({month_pattern})\s+(\d{{4}}|Present|Current)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(19\d{2}|20\d{2})\s*(?:-|–|—|to)\s*"
            r"(19\d{2}|20\d{2}|Present|Current)\b",
            re.IGNORECASE,
        ),
    ]

    for pattern_index, pattern in enumerate(date_patterns):

        for match in pattern.finditer(experience_text):

            try:
                if pattern_index == 0:

                    start_month = datetime.strptime(
                        match.group(1)[:3], "%b"
                    ).month

                    start_year = int(match.group(2))
                    end_month_text = match.group(3)
                    end_year_text = match.group(4)

                    if end_year_text.lower() in {"present", "current"}:
                        end_month = now.month
                        end_year = now.year
                    else:
                        end_month = datetime.strptime(
                            end_month_text[:3], "%b"
                        ).month

                        end_year = int(end_year_text)

                else:
                    start_year = int(match.group(1))
                    end_year_text = match.group(2)
                    start_month = 1

                    if end_year_text.lower() in {"present", "current"}:
                        end_month = now.month
                        end_year = now.year
                    else:
                        end_month = 12
                        end_year = int(end_year_text)

                months = (
                    (end_year - start_year) * 12
                    + end_month - start_month + 1
                )

                if 0 < months <= 600:
                    total_months += months

            except (ValueError, TypeError):
                continue

    return round(total_months / 12, 1)


# --------------------------------------------------
# EDUCATION
# --------------------------------------------------

def extract_education(text: str) -> list[str]:
    """Extract common degree names."""

    if not text:
        return []

    patterns = [
        r"\bB\.?\s?Tech\b[^\n,;]*",
        r"\bB\.?\s?E\.?\b[^\n,;]*",
        r"\bB\.?\s?Sc\.?\b[^\n,;]*",
        r"\bM\.?\s?Tech\b[^\n,;]*",
        r"\bM\.?\s?E\.?\b[^\n,;]*",
        r"\bM\.?\s?Sc\.?\b[^\n,;]*",
        r"\bBCA\b[^\n,;]*",
        r"\bMCA\b[^\n,;]*",
        r"\bMBA\b[^\n,;]*",
        r"\bPh\.?\s?D\.?\b[^\n,;]*",
        r"\bBachelor(?:'s)?\s+(?:degree|of\s+[^,\n;]+)[^\n,;]*",
        r"\bMaster(?:'s)?\s+(?:degree|of\s+[^,\n;]+)[^\n,;]*",
    ]

    matches = []

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = re.sub(r"\s+", " ", match.group(0)).strip(" -|")

            if value:
                matches.append((match.start(), value))

    results = []
    seen = set()

    for _, value in sorted(matches, key=lambda item: item[0]):
        key = value.lower()

        if key not in seen:
            seen.add(key)
            results.append(value)

    return results


# --------------------------------------------------
# COMPANIES AND DESIGNATIONS
# --------------------------------------------------

def extract_companies(text: str) -> list[str]:
    """Extract companies from a dedicated section and work experience."""

    companies = []

    if not text:
        return []

    # 1. Extract companies from PREVIOUS COMPANIES section
    previous_section = extract_section(text, "PREVIOUS COMPANIES")

    for line in previous_section:
        line = re.sub(r"^[\s•*\-]+", "", line).strip()

        if not line:
            continue

        # Support comma-separated company names
        values = re.split(r"[,;|]", line)

        for value in values:
            company = value.strip(" -•|")

            if company and company.lower() not in {
                item.lower() for item in companies
            }:
                companies.append(company)

    # 2. Extract companies from PROFESSIONAL EXPERIENCE
    experience_text = get_work_experience_text(text)

    for line in experience_text.splitlines():

        patterns = [
            r"\bat\s+(.+?)(?:\s*\(|\s*[-–—]\s*|:|$)",
            r"^\s*(?:company|organization|employer)\s*:\s*(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)

            if match:
                company = match.group(1).strip(" ,.-")

                if company and company.lower() not in {
                    item.lower() for item in companies
                }:
                    companies.append(company)

                break

    return companies


def extract_designations(text: str) -> list[str]:
    """Extract likely job titles."""

    titles = [
        "senior software engineer",
        "software engineer",
        "software developer",
        "python developer",
        "backend engineer",
        "backend developer",
        "junior developer",
        "application developer",
        "lead engineer",
        "machine learning engineer",
        "full stack developer",
        "frontend developer",
        "web developer",
        "data analyst",
        "data scientist",
        "AI engineer",
        "project manager",
        "business analyst",
        "system engineer",
        "technical lead",
        "team lead",
        "intern",
    ]

    found = []
    experience_text = get_work_experience_text(text or "")

    for line in experience_text.splitlines():

        role_part = re.split(
            r"\s+at\s+",
            line,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        for title in sorted(titles, key=len, reverse=True):

            if re.search(
                r"(?<!\w)" + re.escape(title) + r"(?!\w)",
                role_part,
                re.IGNORECASE,
            ):

                display = title.title()

                if display.lower() not in {
                    item.lower() for item in found
                }:
                    found.append(display)

                break

    for line in (text or "").splitlines():

        match = re.search(
            r"^\s*designation\s*[:\-]\s*(.+)$",
            line,
            re.IGNORECASE,
        )

        if match:
            value = match.group(1).strip()

            if value and value.lower() not in {
                item.lower() for item in found
            }:
                found.append(value)

    return found


# --------------------------------------------------
# CERTIFICATIONS AND PROJECTS
# --------------------------------------------------

def extract_certifications(text: str) -> list[str]:
    """Extract certifications."""

    return (
        extract_section(text or "", "CERTIFICATIONS")
        or extract_section(text or "", "CERTIFICATES")
    )


def extract_projects(text: str) -> list[str]:
    """Extract projects."""

    return (
        extract_section(text or "", "PROJECTS")
        or extract_section(text or "", "PERSONAL PROJECTS")
    )


# --------------------------------------------------
# MAIN CANDIDATE EXTRACTION FUNCTION
# --------------------------------------------------

def extract_candidate_info(text: str) -> dict[str, Any]:
    """Extract all candidate information from resume text."""

    text = text or ""

    technical_skills = extract_skills(text)

    candidate_info = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "technical_skills": technical_skills,
        "skills": technical_skills,
        "functional_skills": extract_functional_skills(text),
        "experience_years": extract_experience(text),
        "education": extract_education(text),
        "previous_companies": extract_companies(text),
        "designations": extract_designations(text),
        "certifications": extract_certifications(text),
        "projects": extract_projects(text),
    }

    return candidate_info