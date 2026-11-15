import numpy as np

from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load the AI model only once
@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def calculate_skill_score(candidate_skills, required_skills):
    """Calculate the percentage of required skills matched."""

    candidate_skills = {
        skill.lower() for skill in candidate_skills
    }

    required_skills = {
        skill.lower() for skill in required_skills
    }

    matched_skills = sorted(
        candidate_skills.intersection(required_skills)
    )

    missing_skills = sorted(
        required_skills - candidate_skills
    )

    if not required_skills:
        score = 100.0
    else:
        score = (
            len(matched_skills) / len(required_skills)
        ) * 100

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_score": round(score, 2)
    }



def calculate_semantic_similarity(resume_text, jd_text):
    """Compare resume and job description using AI embeddings."""

    model = get_model()

    embeddings = model.encode(
        [resume_text, jd_text],
        convert_to_numpy=True
    )

    resume_embedding = np.asarray(
        embeddings[0]
    ).reshape(1, -1)

    jd_embedding = np.asarray(
        embeddings[1]
    ).reshape(1, -1)

    similarity = cosine_similarity(
        resume_embedding,
        jd_embedding
    )[0][0]

    similarity_score = max(
        0.0, min(1.0, float(similarity))
    ) * 100

    return round(similarity_score, 2)


def calculate_experience_score(
    candidate_experience,
    required_experience
):
    """Compare candidate experience with job requirements."""

    if required_experience is None:
        return 100.0

    if candidate_experience is None:
        return 0.0

    if required_experience <= 0:
        return 100.0

    score = (
        candidate_experience / required_experience
    ) * 100

    return round(min(score, 100), 2)


def calculate_matching_score(
    resume_text,
    candidate_info,
    jd_text,
    jd_requirements
):
    """Calculate the overall resume matching score."""

    # 1. Skill matching
    skill_result = calculate_skill_score(
        candidate_info.get("skills", []),
        jd_requirements.get("required_skills", [])
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

    # 4. Weighted overall score
    overall_score = (
        skill_result["skill_score"] * 0.50
        + semantic_score * 0.30
        + experience_score * 0.20
    )

    # 5. Explain the result
    reasons = [
        f"Matched {len(skill_result['matched_skills'])} "
        f"out of {len(jd_requirements.get('required_skills', []))} "
        "required skills.",
        f"Semantic similarity score: {semantic_score}%.",
        f"Experience matching score: {experience_score}%."
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
        "semantic_similarity": semantic_score,
        "experience_score": experience_score,
        "candidate_experience_years": candidate_info.get(
            "experience_years"
        ),
        "required_experience_years": jd_requirements.get(
            "required_experience_years"
        ),
        "reasons": reasons
    }
