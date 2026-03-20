import streamlit as st
import fitz
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ GROQ_API_KEY not found in .env file!")
    st.stop()

client = Groq(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_resume(resume_text, job_description):
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and career coach.
    
    Analyze this resume against the job description and provide:
    1. ATS Score (0-100)
    2. Top 5 Strengths
    3. Top 5 Areas to Improve
    4. Missing Keywords from job description
    5. Overall Recommendation
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Format your response clearly with headers for each section.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content

def show_resume_analyzer():
    st.title("📄 Resume Analyzer")
    st.markdown("Upload your resume and get an AI-powered ATS score with improvement tips!")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload Your Resume")
        pdf_file = st.file_uploader("Choose your resume (PDF only)", type=["pdf"])

    with col2:
        st.subheader("Paste Job Description")
        job_description = st.text_area(
            "Copy and paste the job description here",
            height=200,
            placeholder="Paste the job description you are applying for..."
        )

    if st.button("🔍 Analyze My Resume", type="primary"):
        if pdf_file is None:
            st.error("Please upload your resume PDF!")
        elif not job_description:
            st.error("Please paste a job description!")
        else:
            with st.spinner("🤖 AI is analyzing your resume..."):
                resume_text = extract_text_from_pdf(pdf_file)
                result = analyze_resume(resume_text, job_description)

            st.success("✅ Analysis Complete!")
            st.markdown("---")
            st.markdown(result)

            st.download_button(
                label="📥 Download Analysis",
                data=result,
                file_name="resume_analysis.txt",
                mime="text/plain"
            )