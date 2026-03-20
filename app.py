import streamlit as st

st.set_page_config(
    page_title="AI Career Intelligence Platform",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Career Intelligence Platform")
st.markdown("### Your AI-powered career assistant")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "🏠 Home",
    "📄 Resume Analyzer",
    "🔍 Job Scraper",
    "✉️ Email Generator",
    "📊 Dashboard"
])

if page == "🏠 Home":
    st.markdown("""
    ## Welcome! 👋
    This platform helps you:
    - 📄 **Analyze your resume** and get ATS score
    - 🔍 **Find live jobs** matching your skills
    - ✉️ **Generate cold emails** to recruiters
    - 📊 **Explore job market** trends
    """)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Resume Score", "0%", "Upload resume")
    col2.metric("Jobs Found", "0", "Scrape jobs")
    col3.metric("Emails Generated", "0", "Generate now")
    col4.metric("Skills Matched", "0", "Analyze now")

elif page == "📄 Resume Analyzer":
    from resume_analyzer import show_resume_analyzer
    show_resume_analyzer()

elif page == "🔍 Job Scraper":
    from job_scraper import show_job_scraper
    show_job_scraper()

elif page == "✉️ Email Generator":
    from email_generator import show_email_generator
    show_email_generator()

elif page == "📊 Dashboard":
    from dashboard import show_dashboard
    show_dashboard()