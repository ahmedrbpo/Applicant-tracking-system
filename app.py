import streamlit as st
from docx import Document
import PyPDF2
import re
from rake_nltk import Rake

# --- Helper functions ---

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

def extract_keywords_from_jd_rake(text, top_n=50):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    phrases = rake.get_ranked_phrases()
    # Return top N phrases, normalized
    return set([phrase.lower() for phrase in phrases[:top_n]])

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
    score = (len(matched) / len(jd_keywords) * 100) if jd_keywords else 0
    return matched, missing, score


# --- Streamlit UI ---

st.title("ATS Resume Analyzer - Keyword Matching with RAKE")

jd_text = st.text_area("Paste the Job Description (JD) here", height=300)

custom_kw_input = st.text_input("Add Custom Keywords (comma-separated, optional)")

resume_file = st.file_uploader("Upload Resume (.docx or .pdf)", type=["docx", "pdf"])

if st.button("Analyze"):

    if not jd_text.strip() and not custom_kw_input.strip():
        st.warning("Please paste a Job Description or enter custom keywords for analysis.")
        st.stop()

    if not resume_file:
        st.error("Please upload a resume file (.docx or .pdf) to analyze.")
        st.stop()

    # Extract JD keywords using RAKE if JD text provided
    jd_keywords = extract_keywords_from_jd_rake(jd_text) if jd_text.strip() else set()

    # Extract custom keywords from user input
    custom_keywords = set()
    if custom_kw_input.strip():
        # Normalize and split
        custom_keywords = set([kw.strip().lower() for kw in custom_kw_input.split(",") if kw.strip()])

    # Combined keywords for matching
    combined_keywords = jd_keywords.union(custom_keywords)

    if not combined_keywords:
        st.warning("No keywords extracted or provided. Please check your input.")
        st.stop()

    # Extract resume text
    if resume_file.name.endswith(".docx"):
        resume_text = extract_text_from_docx(resume_file)
    elif resume_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume_file)
    else:
        st.error("Unsupported file type. Use .docx or .pdf only.")
        st.stop()

    # Extract matched keywords in resume text
    matched_keywords = extract_keywords_from_text(resume_text, combined_keywords)

    # Compute matching stats
    matched, missing, score = match_keywords(combined_keywords, matched_keywords)

    # Display results
    st.write(f"**ATS Match Score:** {score:.2f}%")
    st.write("### Matched Keywords:")
    st.write(", ".join(sorted(matched)) if matched else "None")

    st.write("### Missing Keywords:")
    st.write(", ".join(sorted(missing)) if missing else "None")


# Optional: show extracted RAKE keywords separately for info/debug
if jd_text.strip():
    st.write("### Extracted Keywords from JD using RAKE (Top 20):")
    extracted = extract_keywords_from_jd_rake(jd_text, top_n=20)
    st.write(", ".join(sorted(extracted)))
