from app.services.candidate_extractor import extract_companies

resume_text = """
AARAV MEHTA

PREVIOUS COMPANIES
Northstar Technologies
ABC Software Solutions

PROFESSIONAL EXPERIENCE
Python Developer at Northstar Technologies
Backend Developer at ABC Software Solutions

EDUCATION
B.E. Computer Science
"""

result = extract_companies(resume_text)

print("Extracted Previous Companies:", result)