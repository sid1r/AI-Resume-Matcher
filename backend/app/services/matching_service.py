
import re
from functools import lru_cache

from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# AI MODEL
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_model():
    """Load the sentence transformer model only once."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

def normalize_skill(skill):
    """Normalize skill names before comparison."""

    skill = skill.lower().strip()
    skill = re.sub(r"\s+", " ", skill)

    aliases = {
    "restapi": "rest api",
    "rest apis": "rest api",
    "scikit learn": "scikit-learn",
    "js": "javascript"
}

    return aliases.get(skill, skill)


# --------------------------------------------------
# TECHNICAL SKILL MATCHING
# --------------------------------------------------


def calculate_skill_score(
    candidate_skills,
    required_skills,
    required_skill_groups=None
):
    """Calculate technical skill score with OR-based alternatives."""

    candidate_skills = {
        normalize_skill(skill)
        for skill in candidate_skills
    }

    required_skills = {
        normalize_skill(skill)
        for skill in required_skills
    }

    required_skill_groups = required_skill_groups or []

    normalized_groups = [
        {
            normalize_skill(skill)
            for skill in group
        }
        for group in required_skill_groups
        if group
    ]

    # Remove alternatives from individual requirements.
    grouped_skills = set()

    for group in normalized_groups:
        grouped_skills.update(group)

    individual_requirements = required_skills - grouped_skills

    matched_skills = set()
    missing_skills = []
    matched_requirement_count = 0
    total_requirement_count = 0

    # Check individual requirements.
    for skill in sorted(individual_requirements):
        total_requirement_count += 1

        if skill in candidate_skills:
            matched_skills.add(skill)
            matched_requirement_count += 1
        else:
            missing_skills.append(skill)

    # Check OR-based groups.
    for group in normalized_groups:
        total_requirement_count += 1

        matched_options = candidate_skills.intersection(group)

        if matched_options:
            matched_skills.update(matched_options)
            matched_requirement_count += 1
        else:
            missing_skills.append(" or ".join(sorted(group)))

    if total_requirement_count == 0:
        score = 100.0
    else:
        score = (
            matched_requirement_count / total_requirement_count
        ) * 100

    return {
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "skill_score": round(score, 2),
        "matched_requirement_count": matched_requirement_count,
        "total_requirement_count": total_requirement_count
    }



# --------------------------------------------------
# FUNCTIONAL SKILL MATCHING
# --------------------------------------------------

def calculate_functional_skill_score(
    candidate_skills,
    required_skills
):
    """Calculate functional skill matching percentage."""

    return calculate_skill_score(
        candidate_skills,
        required_skills
    )


# --------------------------------------------------
# SEMANTIC SIMILARITY
# --------------------------------------------------

def calculate_semantic_similarity(resume_text, jd_text):
    """Compare resume and job description using AI embeddings."""

    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    model = get_model()

    embeddings = model.encode(
        [resume_text, jd_text],
        convert_to_numpy=True
    )

    similarity = cosine_similarity(
        embeddings[0].reshape(1, -1),
        embeddings[1].reshape(1, -1)
    )[0][0]

    similarity_score = max(
        0.0,
        min(1.0, float(similarity))
    ) * 100

    return round(similarity_score, 2)


# --------------------------------------------------
# EXPERIENCE MATCHING
# --------------------------------------------------

def calculate_experience_score(
    candidate_experience,
    required_experience
):
    """Compare candidate experience with job requirements."""

    if required_experience is None or required_experience <= 0:
        return 100.0

    if candidate_experience is None:
        return 0.0

    score = (
        candidate_experience / required_experience
    ) * 100

    return round(min(score, 100), 2)


# --------------------------------------------------
# EDUCATION MATCHING
# --------------------------------------------------

DEGREE_LEVELS = {
    "bachelor": 1,
    "master": 2,
    "phd": 3
}

DEGREE_ALIASES = {
    "b.tech": "bachelor",
    "b.e.": "bachelor",
    "b.sc": "bachelor",
    "bca": "bachelor",
    "bachelor": "bachelor",

    "m.tech": "master",
    "m.e.": "master",
    "m.sc": "master",
    "mca": "master",
    "mba": "master",
    "master": "master",

    "phd": "phd"
}

EDUCATION_FIELDS = {
    "computer science": [
        "computer science",
        "cs"
    ],
    "information technology": [
        "information technology",
        "it"
    ],
    "information science": [
        "information science",
        "is"
    ],
    "computer applications": [
        "computer applications"
    ],
    "software engineering": [
        "software engineering"
    ],
    "mathematics": [
        "mathematics",
        "mathematical"
    ]
}


def get_degree_level(education_text):
    """Identify the highest degree level in education text."""

    text = education_text.lower()

    # Check PhD first
    if re.search(r"\bph\.?d\b|\bdoctorate\b", text):
        return "phd"

    # Check postgraduate degrees
    postgraduate_patterns = [
        r"\bm\.?\s*tech\b",
        r"\bm\.?\s*e\.?\b",
        r"\bm\.?\s*sc\.?\b",
        r"\bmca\b",
        r"\bmba\b",
        r"\bmaster\b"
    ]

    if any(re.search(pattern, text) for pattern in postgraduate_patterns):
        return "master"

    # Check undergraduate degrees
    undergraduate_patterns = [
        r"\bb\.?\s*tech\b",
        r"\bb\.?\s*e\.?\b",
        r"\bb\.?\s*sc\.?\b",
        r"\bbca\b",
        r"\bbachelor\b"
    ]

    if any(re.search(pattern, text) for pattern in undergraduate_patterns):
        return "bachelor"

    return None


def get_education_fields(education_text):
    """Identify specialization or subject fields."""

    text = education_text.lower()
    found_fields = []

    for field, aliases in EDUCATION_FIELDS.items():
        for alias in aliases:

            # Match abbreviations as whole words
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"

            if re.search(pattern, text):
                found_fields.append(field)
                break

    return found_fields


def calculate_education_score(
    candidate_education,
    required_qualifications
):
    """
    Compare education requirements.

    Degree levels are treated as minimum requirements.
    Multiple subject fields are treated as alternatives:
    matching any one accepted field is sufficient.
    """

    candidate_education = [
        str(item).lower().strip()
        for item in candidate_education
        if item
    ]

    required_qualifications = [
        str(item).lower().strip()
        for item in required_qualifications
        if item
    ]

    if not required_qualifications:
        return {
            "matched_qualifications": [],
            "missing_qualifications": [],
            "education_score": 100.0
        }

    # Identify candidate degree levels and fields
    candidate_degree_levels = [
        get_degree_level(item)
        for item in candidate_education
    ]

    candidate_degree_levels = [
        level for level in candidate_degree_levels
        if level
    ]

    candidate_fields = set()

    for education in candidate_education:
        candidate_fields.update(
            get_education_fields(education)
        )

    # Separate degree requirements from subject requirements
    required_degree = None
    required_fields = []
    other_requirements = []

    for qualification in required_qualifications:

        if qualification in DEGREE_ALIASES:
            level = DEGREE_ALIASES[qualification]

            if (
                required_degree is None
                or DEGREE_LEVELS[level] > DEGREE_LEVELS[required_degree]
            ):
                required_degree = level

        elif qualification in EDUCATION_FIELDS:
            required_fields.append(qualification)

        else:
            other_requirements.append(qualification)

    matched = []
    missing = []

    # Check minimum degree level
    if required_degree:

        required_level = DEGREE_LEVELS[required_degree]

        candidate_level = max(
            (
                DEGREE_LEVELS[level]
                for level in candidate_degree_levels
            ),
            default=0
        )

        if candidate_level >= required_level:
            matched.append(required_degree)
        else:
            missing.append(required_degree)

    # Check accepted subject fields.
    # Any one matching field satisfies this group.
    if required_fields:

        matched_fields = [
            field for field in required_fields
            if field in candidate_fields
        ]

        if matched_fields:
            matched.extend(matched_fields)
        else:
            missing.extend(required_fields)

    # Check any additional qualification keywords
    for requirement in other_requirements:

        if any(
            requirement in education
            for education in candidate_education
        ):
            matched.append(requirement)
        else:
            missing.append(requirement)

    total_groups = (
        (1 if required_degree else 0)
        + (1 if required_fields else 0)
        + len(other_requirements)
    )

    matched_groups = (
        (1 if required_degree and required_degree in matched else 0)
        + (1 if required_fields and any(
            field in matched for field in required_fields
        ) else 0)
        + sum(
            1 for requirement in other_requirements
            if requirement in matched
        )
    )

    score = (
        matched_groups / total_groups
    ) * 100 if total_groups else 100.0

    return {
        "matched_qualifications": sorted(set(matched)),
        "missing_qualifications": sorted(set(missing)),
        "education_score": round(score, 2)
    }


# --------------------------------------------------
# OVERALL MATCHING SCORE
# --------------------------------------------------

def calculate_matching_score(
    resume_text,
    candidate_info,
    jd_text,
    jd_requirements
):
    """Calculate the overall resume matching score."""

    # 1. Technical skill matching
    skill_result = calculate_skill_score(
    candidate_info.get(
        "technical_skills",
        candidate_info.get("skills", [])
    ),
    jd_requirements.get("required_skills", []),
    jd_requirements.get("required_skill_groups", [])
)

    # 2. Semantic similarity
    semantic_score = calculate_semantic_similarity(
        resume_text,
        jd_text
    )

    # 3. Experience matching
    experience_score = calculate_experience_score(
        candidate_info.get("experience_years"),
        jd_requirements.get("required_experience_years")
    )

    # 4. Education matching
    education_result = calculate_education_score(
        candidate_info.get("education", []),
        jd_requirements.get("required_qualifications", [])
    )

    # 5. Functional skill matching
    functional_result = calculate_functional_skill_score(
        candidate_info.get("functional_skills", []),
        jd_requirements.get("required_functional_skills", [])
    )

    # 6. Weighted overall score
    overall_score = (
        skill_result["skill_score"] * 0.40
        + semantic_score * 0.20
        + experience_score * 0.20
        + education_result["education_score"] * 0.10
        + functional_result["skill_score"] * 0.10
    )

    # 7. Explanation
    reasons = [
        (
    f"Matched {skill_result['matched_requirement_count']} "
    f"out of {skill_result['total_requirement_count']} "
    "technical skill requirements."
),
        f"Semantic similarity score: {semantic_score}%.",
        f"Experience matching score: {experience_score}%.",
        f"Education matching score: {education_result['education_score']}%.",
        (
            f"Matched {len(functional_result['matched_skills'])} "
            f"out of {len(jd_requirements.get('required_functional_skills', []))} "
            "required functional skills."
        )
    ]

    if candidate_info.get("experience_years") is None:
        reasons.append(
            "Candidate experience could not be identified in the resume."
        )

    return {
        "overall_matching_score": round(overall_score, 2),

        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "skill_score": skill_result["skill_score"],

        "matched_requirement_count": skill_result["matched_requirement_count"],
        "total_requirement_count": skill_result["total_requirement_count"],

        "matched_functional_skills": functional_result["matched_skills"],
        "missing_functional_skills": functional_result["missing_skills"],
        "functional_skill_score": functional_result["skill_score"],

        "semantic_similarity": semantic_score,

        "experience_score": experience_score,
        "candidate_experience_years": candidate_info.get("experience_years"),
        "required_experience_years": jd_requirements.get(
            "required_experience_years"
        ),

        "matched_qualifications": education_result["matched_qualifications"],
        "missing_qualifications": education_result["missing_qualifications"],
        "education_score": education_result["education_score"],

        "reasons": reasons
    }
