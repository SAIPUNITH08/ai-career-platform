import streamlit as st
import requests
import pandas as pd
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
REED_API_KEY = os.getenv("REED_API_KEY")

def get_reed_jobs(job_title, location=""):
    jobs = []
    try:
        url = "https://www.reed.co.uk/api/1.0/search"
        params = {
            "keywords": job_title,
            "locationName": location,
            "resultsToTake": 10
        }
        response = requests.get(
            url,
            params=params,
            auth=(REED_API_KEY, ""),
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            for job in data.get("results", []):
                jobs.append({
                    "Job Title": job.get("jobTitle", "N/A"),
                    "Company": job.get("employerName", "N/A"),
                    "Location": job.get("locationName", "N/A"),
                    "Salary": f"£{job.get('minimumSalary', 'N/A')} - £{job.get('maximumSalary', 'N/A')}",
                    "Description": job.get("jobDescription", "N/A")[:300] + "...",
                    "Link": f"https://www.reed.co.uk/jobs/{job.get('jobId', '')}",
                    "Posted": job.get("date", "N/A")[:10],
                    "Source": "Reed.co.uk ✅"
                })
        else:
            st.error(f"Reed API error: {response.status_code}")
    except Exception as e:
        st.error(f"Reed error: {e}")
    return jobs

def get_ai_jobs_fallback(job_title, location, num_jobs=8):
    prompt = f"""
    Generate {num_jobs} realistic job listings for "{job_title}" jobs in "{location}".
    Return ONLY a JSON array with no extra text:
    [
      {{
        "Job Title": "Senior Python Developer",
        "Company": "TCS",
        "Location": "Bangalore, India",
        "Salary": "₹8,00,000 - ₹15,00,000 per year",
        "Skills": "Python, Django, REST APIs, PostgreSQL",
        "Experience": "3-5 years",
        "Type": "Full-time",
        "Description": "We are looking for a Python developer...",
        "Source": "AI Generated"
      }}
    ]
    Use realistic Indian companies and salaries. Return ONLY valid JSON.
    """
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def get_market_insights(jobs, job_title):
    if not jobs:
        return "No jobs to analyze."
    jobs_text = "\n".join([
        f"- {j.get('Job Title')} at {j.get('Company')} | {j.get('Location')}"
        for j in jobs[:6]
    ])
    prompt = f"""
    Based on these {job_title} job listings:
    {jobs_text}
    
    Provide:
    1. 🔥 Top 5 most in-demand skills
    2. 📈 Market trend in 2025
    3. 💰 Salary ranges (fresher/mid/senior)
    4. 🏢 Top companies hiring
    5. 💡 3 tips to get hired faster
    Keep it concise and actionable.
    """
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

def show_job_scraper():
    st.title("🔍 Live Job Finder")
    st.markdown("Real jobs from **Reed.co.uk** + AI-powered market insights!")

    col1, col2, col3 = st.columns(3)
    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g. Python Developer")
    with col2:
        location = st.text_input("Location", placeholder="e.g. London")
    with col3:
        source = st.selectbox("Source", [
            "🌐 Reed (Real Jobs)",
            "🤖 AI Generated"
        ])

    if st.button("🔍 Find Jobs", type="primary"):
        if not job_title:
            st.error("Please enter a job title!")
            return

        all_jobs = []

        with st.spinner("🔍 Fetching live jobs..."):
            if source == "🌐 Reed (Real Jobs)":
                if not REED_API_KEY:
                    st.error("❌ REED_API_KEY not found in .env file!")
                    return
                all_jobs = get_reed_jobs(job_title, location)
                if not all_jobs:
                    st.warning("No Reed jobs found. Switching to AI mode...")
                    all_jobs = get_ai_jobs_fallback(job_title, location)
            else:
                all_jobs = get_ai_jobs_fallback(job_title, location)

        if all_jobs:
            st.success(f"🎉 Found {len(all_jobs)} jobs!")
            st.markdown("---")

            for job in all_jobs:
                with st.expander(
                    f"🏢 {job.get('Job Title')} — {job.get('Company')} | 📍 {job.get('Location')} | {job.get('Source', '')}"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**💰 Salary:** {job.get('Salary', 'N/A')}")
                        st.write(f"**📅 Posted:** {job.get('Posted', 'N/A')}")
                    with col2:
                        link = job.get('Link', '#')
                        if link and link != 'N/A':
                            st.markdown(f"[🔗 Apply Now]({link})")
                    st.write(f"**📝 Description:** {job.get('Description', 'N/A')}")

            st.markdown("---")
            df = pd.DataFrame(all_jobs)
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Jobs CSV",
                csv, f"{job_title}_jobs.csv", "text/csv"
            )

            st.subheader("🤖 AI Market Insights")
            with st.spinner("Analyzing market trends..."):
                insights = get_market_insights(all_jobs, job_title)
            st.markdown(insights)
        else:
            st.warning("No jobs found. Try different keywords!")