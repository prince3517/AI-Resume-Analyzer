import re
from typing import List, Dict

COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    "sql", "mysql", "postgresql", "mongodb", "oracle",
    "flask", "django", "fastapi", "react", "angular", "node.js",
    "html", "css", "git", "github", "docker", "kubernetes",
    "aws", "azure", "gcp", "linux", "rest api", "restful api",
    "machine learning", "deep learning", "artificial intelligence",
    "tensorflow", "pytorch", "keras", "scikit-learn", "nlp",
    "pandas", "numpy", "power bi", "tableau", "excel",
    "communication", "leadership", "sales", "customer service",
    "data analysis", "data visualization", "statistics", "agile",
]

DEFAULT_THRESHOLD = 85.0
THRESHOLD = DEFAULT_THRESHOLD


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str) -> List[str]:
    normalized = normalize(text)
    return sorted({
        skill for skill in COMMON_SKILLS
        if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", normalized)
    })


def extract_years_experience(text: str):
    normalized = normalize(text)
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]
    values = []
    for pattern in patterns:
        values += [float(x) for x in re.findall(pattern, normalized)]
    return max(values) if values else None


_MODEL = None


def get_embedding_model():
    global _MODEL

    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        print("Loading AI model...")
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        print("AI model loaded successfully.")

    return _MODEL


def semantic_similarity(resume_text: str, jd_text: str) -> float:
    try:
        from sklearn.metrics.pairwise import cosine_similarity

        model = get_embedding_model()

        embeddings = model.encode([
            resume_text[:12000],
            jd_text[:12000]
        ])

        similarity = float(
            cosine_similarity(
                [embeddings[0]],
                [embeddings[1]]
            )[0][0]
        )

        return max(0, min(1, similarity)) * 100

    except Exception as exc:
        print(f"AI semantic model unavailable: {exc}")
        print("Using TF-IDF fallback...")

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        matrix = TfidfVectorizer(
            stop_words="english"
        ).fit_transform([
            resume_text,
            jd_text
        ])

        similarity = float(
            cosine_similarity(
                matrix[0:1],
                matrix[1:2]
            )[0][0]
        )

        return max(0, min(1, similarity)) * 100


def analyze_match(resume_text: str, jd_text: str, threshold: float = DEFAULT_THRESHOLD) -> Dict:
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched = sorted(set(resume_skills) & set(jd_skills))
    missing = sorted(set(jd_skills) - set(resume_skills))

    skill_score = 100 if not jd_skills else len(matched) / len(jd_skills) * 100

    required_exp = extract_years_experience(jd_text)
    actual_exp = extract_years_experience(resume_text)
    if required_exp is None:
        experience_score = 100
    elif actual_exp is None:
        experience_score = 0
    else:
        experience_score = min(actual_exp / required_exp, 1) * 100

    edu_terms = [
        "bachelor", "master", "b.sc", "bsc", "b.tech", "m.tech",
        "degree", "computer science", "engineering"
    ]
    jd_norm = normalize(jd_text)
    resume_norm = normalize(resume_text)
    education_required = any(t in jd_norm for t in edu_terms)
    education_score = (
        100 if not education_required or any(t in resume_norm for t in edu_terms)
        else 0
    )

    semantic_score = semantic_similarity(resume_text, jd_text)

    # V2 weighting:
    # skills 50%, experience 20%, education 10%, semantic 20%.
    score = (
        skill_score * .50 +
        experience_score * .20 +
        education_score * .10 +
        semantic_score * .20
    )
    score = round(max(0, min(100, score)), 2)

    reasons = []
    if missing:
        reasons.append("Missing required skills: " + ", ".join(missing))
    if required_exp is not None and (actual_exp is None or actual_exp < required_exp):
        actual = "not clearly stated" if actual_exp is None else f"{actual_exp:g} years"
        reasons.append(f"Required experience: {required_exp:g}+ years; resume indicates {actual}.")
    if education_score == 0:
        reasons.append("Required education/degree information was not clearly found.")
    if semantic_score < 45:
        reasons.append("Resume and job description have relatively low semantic similarity.")
    if not reasons and score < threshold:
        reasons.append("The weighted overall score is below the configured shortlist threshold.")

    return {
        "score": score,
        "shortlisted": score >= threshold,
        "threshold": threshold,
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills": resume_skills,
        "job_skills": jd_skills,
        "skill_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "semantic_score": round(semantic_score, 2),
        "reasons": reasons,
    }
