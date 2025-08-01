import streamlit as st
from docx import Document
import PyPDF2
import re

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[\W_]+', ' ', text)  # Replace non-alphanumeric chars with space
    return text

def extract_keywords_from_jd(text):
    # Basic keyword/phrase extraction by splitting
    # You can improve this with spaCy or RAKE for better quality
    normalized = normalize_text(text)
    words = normalized.split()
    keywords = set()

    # Collect unigrams, bigrams, trigrams as candidate keywords
    for i in range(len(words)):
        keywords.add(words[i])
        if i + 1 < len(words):
            keywords.add(f"{words[i]} {words[i+1]}")
        if i + 2 < len(words):
            keywords.add(f"{words[i]} {words[i+1]} {words[i+2]}")

    # Optionally, filter out stop words or very short words here in production
    return keywords

def extract_keywords_from_text(text, keywords):
    text_norm = normalize_text(text)
    found_keywords = set()
    for kw in keywords:
        kw_norm = normalize_text(kw)
        if kw_norm in text_norm:
            found_keywords.add(kw)
    return found_keywords

def match_keywords(jd_keywords, resume_keywords):
    matched = jd_keywords.intersection(resume_keywords)
    missing = jd_keywords - resume_keywords
    score = len(matched) / len(jd_keywords) * 100 if jd_keywords else 0
    return matched, missing, score

st.title("ATS Resume Analyzer - User Keywords & JD Paste")

# Paste JD (optional)
jd_text = st.text_area("Paste the Job Description (optional)")

# Manually add custom keywords (optional)
custom_kw_input = st.text_input("Add Custom Keywords (comma-separated, optional)")

resume_file = st.file_uploader("Upload resume (.docx or .pdf)")

if st.button("Analyze"):
    if resume_file:
        # Extract resume text
        if resume_file.name.endswith(".docx"):
            resume_text = extract_text_from_docx(resume_file)
        elif resume_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        # Extract keywords from pasted JD (if any)
        jd_keywords = extract_keywords_from_jd(jd_text) if jd_text.strip() else set()

        # Extract custom keywords added by user
        custom_keywords = set()
        if custom_kw_input.strip():
            # Split by comma, strip spaces
            custom_keywords = set([kw.strip().lower() for kw in custom_kw_input.split(",") if kw.strip()])

        # Combine JD keywords + custom keywords
        combined_keywords = jd_keywords.union(custom_keywords)

        if not combined_keywords:
            st.warning("Please paste a Job Description or provide custom keywords for matching.")
            st.stop()

        # Extract matched keywords from resume text
        matched_keywords = extract_keywords_from_text(resume_text, combined_keywords)

        # Match and score
        matched, missing, score = match_keywords(combined_keywords, matched_keywords)

        st.write(f"**ATS Match Score:** {score:.2f}%")
        st.write("### Matched Keywords:")
        st.write(", ".join(sorted(matched)) if matched else "None")
        st.write("### Missing Keywords:")
        st.write(", ".join(sorted(missing)) if missing else "None")
    else:
        st.error("Please upload a resume to analyze.")  
        
        st.stop()   
