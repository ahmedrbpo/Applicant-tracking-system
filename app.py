import streamlit as st
from docx import Document
import PyPDF2
import re
import nltk
from rake_nltk import Rake

# Ensure NLTK data is present
nltk.download('stopwords')
nltk.download('punkt')

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[\W_]+', ' ', text)  # Replace non-alphanum chars with space
    return text

def extract_keywords_from_jd_rake(text, top_n=50):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    phrases = rake.get_ranked_phrases()
    return set([phrase.lower().strip() for phrase in phrases[:top_n]])

def streamline_keywords(keywords):
    # Expand these based on your needs
    stopwords = {"job", "candidate", "experience", "years", "looking", "role", "required"}
    streamlined = set()
    for kw in keywords:
        kw_lower = kw.lower().strip()
        if any(sw in kw_lower for sw in stopwords):  # Remove common words
            continue
        if len(kw_lower) < 3:
            continue
        if re.fullmatch(r"[\W\d]+", kw_lower):
            continue
        streamlined.add(kw_lower)
    return set(sorted(streamlined))

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

st.title("ATS Resume Analyzer - Streamlined JD Keyword Matching")

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

    jd_keywords = extract_keywords_from_jd_rake(jd_text) if jd_text.strip() else set()
    # Streamline keywords from JD
    jd_keywords = streamline_keywords(jd_keywords)

    # Extract custom keywords and streamline
    custom_keywords = set()
    if custom_kw_input.strip():
        custom_keywords = set([kw.lower().strip() for kw in custom_kw_input.split(",") if kw.strip()])
    custom_keywords = streamline_keywords(custom_keywords)

    combined_keywords = jd_keywords.union(custom_keywords)
    if not combined_keywords:
        st.warning("No keywords extracted or provided. Please check your input.")
        st.stop()

    # Resume text extraction
    if resume_file.name.endswith(".docx"):
        resume_text = extract_text_from_docx(resume_file)
    elif resume_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume_file)
    else:
        st.error("Unsupported file type. Use .docx or .pdf only.")
        st.stop()

    matched_keywords = extract_keywords_from_text(resume_text, combined_keywords)
    matched, missing, score = match_keywords(combined_keywords, matched_keywords)

    st.write(f"**ATS Match Score:** {score:.2f}%")
    st.write("### Matched Keywords:")
    st.write(", ".join(sorted(matched)) if matched else "None")
    st.write("### Missing Keywords:")
    st.write(", ".join(sorted(missing)) if missing else "None")

    # For transparency: show streamlined JD keywords
    st.write("### Streamlined Extracted Keywords from JD (Top 20):")
    st.write(", ".join(list(jd_keywords)[:20]))
