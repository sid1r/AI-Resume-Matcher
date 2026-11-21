
import re

from app.services.candidate_extractor import (
    SKILLS_LIST,
    FUNCTIONAL_SKILLS
)


def normalize_jd_skill(skill):
    """Normalize common skill-name variations."""
    skill = skill.lower().strip()
    skill = re.sub(r"\s+", " ", skill)

    aliases = {
        "rest apis": "rest api",
        "restapi": "rest api",
        "rest api": "rest api",
        "scikit learn": "scikit-learn",
        "js": "javascript"
    }

    return aliases.get(skill, skill)


def extract_jd_skills(jd_text: str):
    """Extract required technical skills."""
    text = jd_text.lower()
    found_skills = set()

    for skill in SKILLS_LIST:
        normalized = normalize_jd_skill(skill)

        # Handle REST API and REST APIs consistently.
        if normalized == "rest api":
            pattern = r"(?<!\w)rest\s*apis?(?!\w)"
        else:
            pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.add(normalized)

    # Also detect REST API if it is not in SKILLS_LIST.
    if re.search(r"(?<!\w)rest\s*apis?(?!\w)", text):
        found_skills.add("rest api")

    return sorted(found_skills)


def extract_jd_skill_groups(jd_text: str):
    """
    Identify explicitly written technical skill alternatives,
    such as FastAPI or Flask and MySQL or PostgreSQL.
    """
    text = jd_text.lower()
    skills = sorted(
        {normalize_jd_skill(skill) for skill in SKILLS_LIST},
        key=len,
        reverse=True
    )

    # Find skill mentions and their positions.
    matches = []

    for skill in skills:
        if skill == "rest api":
            pattern = r"(?<!\w)rest\s*apis?(?!\w)"
        else:
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        for match in re.finditer(pattern, text):
            matches.append({
                "skill": skill,
                "start": match.start(),
                "end": match.end()
            })

    matches.sort(key=lambda item: item["start"])

    groups = []
    used = set()

    for first, second in zip(matches, matches[1:]):
        between = text[first["end"]:second["start"]]

        # Only group skills explicitly connected by "or".
        if re.search(r"\bor\b", between):
            first_skill = first["skill"]
            second_skill = second["skill"]

            if first_skill != second_skill:
                group = sorted({first_skill, second_skill})

                if group not in groups:
                    groups.append(group)

                used.add(first_skill)
                used.add(second_skill)

    return groups


def extract_jd_functional_skills(jd_text: str):
    """Extract required functional skills."""
    text = jd_text.lower()
    found_skills = []

    for skill in FUNCTIONAL_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill.lower())

    return sorted(set(found_skills))


def extract_jd_experience(jd_text: str):
    """Extract minimum required years of experience."""

    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?\s*\+?\s*years?",
        r"experience\s*(?:required)?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
        r"minimum\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"at least\s+(\d+(?:\.\d+)?)\s*\+?\s*years?"
    ]

    for pattern in patterns:
        match = re.search(pattern, jd_text, re.IGNORECASE)

        if match:
            return float(match.group(1))

    return None


def extract_jd_qualifications(jd_text: str):
    """Extract educational qualification keywords."""

    keywords = [
        "b.tech",
        "b.e.",
        "bachelor",
        "b.sc",
        "bca",
        "m.tech",
        "m.e.",
        "m.sc",
        "mca",
        "master",
        "mba",
        "phd",
        "computer science",
        "information technology",
        "information science",
        "computer applications",
        "software engineering",
        "mathematics"
    ]

    text = jd_text.lower()
    found = []

    for keyword in keywords:
        pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

        if re.search(pattern, text):
            found.append(keyword)

    return found


def analyze_job_description(jd_text: str):
    """Extract all important job requirements."""

    if not jd_text or not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    return {
        "required_skills": extract_jd_skills(jd_text),
        "required_skill_groups": extract_jd_skill_groups(jd_text),
        "required_functional_skills": extract_jd_functional_skills(jd_text),
        "required_experience_years": extract_jd_experience(jd_text),
        "required_qualifications": extract_jd_qualifications(jd_text)
    }
