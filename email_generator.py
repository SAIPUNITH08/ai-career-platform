import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_email(name, role, company, your_name, your_skills, your_experience, email_type, tone, word_limit):
    prompt = f"""
    Write a {tone.lower()} {email_type} email to {name} at {company} for the {role} position.
    
    Sender details:
    - Name: {your_name}
    - Skills: {your_skills}
    - Experience: {your_experience}
    
    Requirements:
    - Word limit: {word_limit} words
    - Tone: {tone}
    - Start with: Subject: ...
    - Then blank line
    - Then: Dear {name},
    - Then the email body
    - End with professional sign-off and {your_name}
    
    Email type instructions:
    {"Impress the recruiter and get an interview call." if email_type == "Cold Outreach" else ""}
    {"Follow up politely after applying 1 week ago." if email_type == "Follow Up" else ""}
    {"Request a referral from a connection at the company." if email_type == "Referral Request" else ""}
    {"Thank them warmly after the interview and reinforce fit." if email_type == "Thank You After Interview" else ""}
    {"Express excitement about receiving the offer." if email_type == "Job Offer Acceptance" else ""}
    {"Decline politely while keeping the relationship." if email_type == "Offer Decline" else ""}
    {"Ask about internship opportunities." if email_type == "Internship Request" else ""}
    {"Network and ask for career advice." if email_type == "Networking" else ""}
    
    Make it human, natural, and NOT generic. Make it stand out.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

def analyze_email(email_text):
    prompt = f"""
    Analyze this professional email and give a score out of 10 for each:
    
    Email:
    {email_text}
    
    Score these 5 things (be strict, max 10 each):
    1. Subject Line Strength
    2. Personalization
    3. Clarity & Conciseness
    4. Call to Action
    5. Overall Impression
    
    Format exactly like this:
    SUBJECT_LINE: X/10 - one line reason
    PERSONALIZATION: X/10 - one line reason
    CLARITY: X/10 - one line reason
    CALL_TO_ACTION: X/10 - one line reason
    OVERALL: X/10 - one line reason
    TOTAL: XX/50
    VERDICT: one sentence overall verdict
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return response.choices[0].message.content

def generate_linkedin_message(name, role, company, your_name, your_skills):
    prompt = f"""
    Write a highly professional and personalized LinkedIn connection request message.
    
    From: {your_name} (has skills in {your_skills})
    To: {name} (works at {company})
    Purpose: Interested in the {role} position
    
    Strict Rules:
    - MUST be under 300 characters total
    - Start with "Hi {name},"
    - Mention 1 specific skill relevant to {role}
    - Mention {company} by name
    - Sound human, warm and confident — NOT robotic
    - End with a clear reason to connect
    - NO generic phrases like "I came across your profile"
    - NO fluff words like "I hope this message finds you well"
    - Make it memorable and stand out from 100 other messages
    
    Return ONLY the message. No quotes. No explanation.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response.choices[0].message.content

def show_email_generator():
    st.title("✉️ AI Email Generator")
    st.markdown("Generate **professional, personalized emails** that actually get replies!")

    tab1, tab2, tab3 = st.tabs([
        "✉️ Email Generator",
        "📊 Email Analyzer",
        "💼 LinkedIn Message"
    ])

    with tab1:
        st.subheader("👤 Your Details")
        col1, col2 = st.columns(2)
        with col1:
            your_name = st.text_input("Your Full Name", placeholder="e.g. Rahul Sharma")
            your_skills = st.text_input("Your Top Skills", placeholder="e.g. Python, React, Machine Learning")
        with col2:
            your_experience = st.text_input("Your Experience", placeholder="e.g. 2 years in full stack development")

        st.markdown("---")
        st.subheader("🎯 Target Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            recruiter_name = st.text_input("Recruiter / HR Name", placeholder="e.g. Priya Mehta")
        with col2:
            company = st.text_input("Company Name", placeholder="e.g. Google India")
        with col3:
            role = st.text_input("Job Role", placeholder="e.g. Senior Python Developer")

        st.markdown("---")
        st.subheader("⚙️ Email Settings")
        col1, col2, col3 = st.columns(3)
        with col1:
            email_type = st.selectbox("Email Type", [
                "Cold Outreach",
                "Follow Up",
                "Referral Request",
                "Thank You After Interview",
                "Job Offer Acceptance",
                "Offer Decline",
                "Internship Request",
                "Networking"
            ])
        with col2:
            tone = st.selectbox("Tone", [
                "Professional",
                "Friendly & Warm",
                "Confident & Bold",
                "Humble & Eager",
                "Formal"
            ])
        with col3:
            word_limit = st.slider("Word Limit", 100, 300, 180, step=20)

        num_versions = st.radio(
            "How many versions?",
            ["1 Version", "2 Versions", "3 Versions"],
            horizontal=True
        )

        if st.button("✨ Generate Email", type="primary", use_container_width=True):
            if not all([your_name, your_skills, recruiter_name, company, role]):
                st.error("⚠️ Please fill in all fields!")
                return

            versions = int(num_versions[0])
            emails = []

            with st.spinner(f"🤖 Writing {versions} version(s) of your email..."):
                for i in range(versions):
                    email = generate_email(
                        recruiter_name, role, company,
                        your_name, your_skills, your_experience,
                        email_type, tone, word_limit
                    )
                    emails.append(email)

            st.success(f"✅ {versions} email(s) generated!")

            for i, email in enumerate(emails):
                if versions > 1:
                    st.subheader(f"📧 Version {i+1}")
                else:
                    st.subheader(f"📧 Your {email_type} Email")

                st.markdown(
                    f'<div style="background:#1e1e2e;padding:20px;border-radius:10px;'
                    f'border-left:4px solid #7c3aed;white-space:pre-wrap;font-size:14px;">'
                    f'{email}</div>',
                    unsafe_allow_html=True
                )

                st.download_button(
                    f"📥 Download Version {i+1}",
                    email,
                    f"email_v{i+1}.txt",
                    "text/plain",
                    key=f"dl_{i}"
                )
                st.markdown("---")

    with tab2:
        st.subheader("📊 Email Quality Analyzer")
        st.markdown("Paste any email below and get an AI score with feedback!")

        email_to_analyze = st.text_area(
            "Paste your email here",
            height=250,
            placeholder="Paste your email here to analyze it..."
        )

        if st.button("🔍 Analyze Email", type="primary", use_container_width=True):
            if not email_to_analyze:
                st.error("Please paste an email to analyze!")
                return

            with st.spinner("🤖 Analyzing your email..."):
                analysis = analyze_email(email_to_analyze)

            lines = analysis.strip().split("\n")
            scores = {}
            verdict = ""

            for line in lines:
                if "SUBJECT_LINE:" in line:
                    scores["📌 Subject Line"] = line.split("SUBJECT_LINE:")[1].strip()
                elif "PERSONALIZATION:" in line:
                    scores["🎯 Personalization"] = line.split("PERSONALIZATION:")[1].strip()
                elif "CLARITY:" in line:
                    scores["💡 Clarity"] = line.split("CLARITY:")[1].strip()
                elif "CALL_TO_ACTION:" in line:
                    scores["📣 Call to Action"] = line.split("CALL_TO_ACTION:")[1].strip()
                elif "OVERALL:" in line:
                    scores["⭐ Overall"] = line.split("OVERALL:")[1].strip()
                elif "TOTAL:" in line:
                    total = line.split("TOTAL:")[1].strip()
                elif "VERDICT:" in line:
                    verdict = line.split("VERDICT:")[1].strip()

            st.success("✅ Analysis Complete!")
            st.markdown("---")

            for category, score in scores.items():
                st.markdown(f"**{category}:** {score}")

            st.markdown("---")
            if "total" in dir():
                st.markdown(f"### 🏆 Total Score: `{total}`")
            if verdict:
                st.info(f"💬 **Verdict:** {verdict}")

    with tab3:
        st.subheader("💼 LinkedIn Connection Message")
        st.markdown("Generate a **short punchy message** for LinkedIn connection requests!")

        col1, col2 = st.columns(2)
        with col1:
            li_your_name = st.text_input("Your Name", placeholder="Rahul Sharma", key="li_name")
            li_skills = st.text_input("Your Skills", placeholder="Python, ML", key="li_skills")
        with col2:
            li_recruiter = st.text_input("Recruiter Name", placeholder="Priya Mehta", key="li_rec")
            li_company = st.text_input("Company", placeholder="Google India", key="li_comp")

        li_role = st.text_input("Role You Want", placeholder="Python Developer", key="li_role")

        if st.button("💼 Generate LinkedIn Message", type="primary", use_container_width=True):
            if not all([li_your_name, li_skills, li_recruiter, li_company, li_role]):
                st.error("Please fill all fields!")
                return

            with st.spinner("Writing your LinkedIn message..."):
                msg = generate_linkedin_message(
                    li_recruiter, li_role, li_company,
                    li_your_name, li_skills
                )

            st.success("✅ LinkedIn Message Ready!")
            st.markdown(
                f'<div style="background:#1e1e2e;padding:20px;border-radius:10px;'
                f'border-left:4px solid #0077b5;font-size:15px;">'
                f'{msg}</div>',
                unsafe_allow_html=True
            )
            char_count = len(msg)
            color = "green" if char_count <= 300 else "red"
            st.markdown(f"**Character count:** :{color}[{char_count}/300]")

            st.download_button(
                "📥 Download Message",
                msg,
                "linkedin_message.txt",
                "text/plain"
            )