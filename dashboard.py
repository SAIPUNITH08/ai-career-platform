import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def show_dashboard():
    st.title("📊 Job Market Dashboard")
    st.markdown("Explore **real-time AI-powered** job market trends and insights!")

    tab1, tab2, tab3 = st.tabs([
        "📈 Market Trends",
        "💰 Salary Insights",
        "🛠️ Skills Analyzer"
    ])

    with tab1:
        st.subheader("📈 Top Job Roles in Demand — India 2025")

        roles = ["Python Dev", "Data Scientist", "ML Engineer",
                 "DevOps", "React Dev", "Cloud Architect",
                 "AI Engineer", "Full Stack", "Cybersecurity", "Product Manager"]
        demand = [95, 92, 90, 88, 85, 83, 91, 87, 78, 75]
        growth = [12, 18, 22, 15, 10, 20, 25, 11, 16, 9]

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=roles, y=demand,
            name="Demand Score",
            marker_color="#7c3aed",
            text=demand,
            textposition="outside"
        ))
        fig1.add_trace(go.Scatter(
            x=roles, y=growth,
            name="YoY Growth %",
            mode="lines+markers",
            line=dict(color="#f59e0b", width=3),
            marker=dict(size=8),
            yaxis="y2"
        ))
        fig1.update_layout(
            title="Job Demand vs Growth Rate",
            yaxis=dict(title="Demand Score"),
            yaxis2=dict(title="Growth %", overlaying="y", side="right"),
            legend=dict(x=0.01, y=0.99),
            height=450,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")
        st.subheader("🏙️ Top Hiring Cities in India")

        cities = ["Bangalore", "Hyderabad", "Mumbai", "Pune",
                  "Chennai", "Delhi NCR", "Kolkata", "Ahmedabad"]
        jobs_count = [45000, 32000, 28000, 25000, 22000, 38000, 12000, 10000]

        fig2 = px.bar(
            x=cities, y=jobs_count,
            title="Number of Open Positions by City",
            color=jobs_count,
            color_continuous_scale="Viridis",
            labels={"x": "City", "y": "Open Positions"}
        )
        fig2.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("📅 Monthly Job Postings Trend 2025")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        postings = [38000, 41000, 45000, 43000, 47000, 52000,
                    49000, 55000, 58000, 62000, 65000, 70000]

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=months, y=postings,
            fill="tozeroy",
            mode="lines+markers",
            line=dict(color="#10b981", width=3),
            fillcolor="rgba(16,185,129,0.2)",
            marker=dict(size=8, color="#10b981")
        ))
        fig3.update_layout(
            title="Job Market Growth Throughout 2025",
            height=350,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            yaxis=dict(title="Job Postings"),
            xaxis=dict(title="Month")
        )
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader("💰 Salary Insights by Role — India 2025")

        col1, col2 = st.columns(2)
        with col1:
            selected_role = st.selectbox("Select Role", [
                "Python Developer",
                "Data Scientist",
                "ML Engineer",
                "DevOps Engineer",
                "React Developer",
                "Cloud Architect",
                "AI Engineer",
                "Full Stack Developer",
                "Cybersecurity Engineer",
                "Product Manager"
            ])
        with col2:
            experience = st.selectbox("Experience Level", [
                "Fresher (0-1 yr)",
                "Junior (1-3 yrs)",
                "Mid (3-5 yrs)",
                "Senior (5-8 yrs)",
                "Lead (8+ yrs)"
            ])

        salary_data = {
            "Python Developer":     [4, 7, 12, 20, 35],
            "Data Scientist":       [5, 8, 14, 22, 38],
            "ML Engineer":          [6, 10, 16, 25, 42],
            "DevOps Engineer":      [5, 8, 13, 21, 36],
            "React Developer":      [4, 7, 11, 18, 30],
            "Cloud Architect":      [7, 11, 18, 28, 50],
            "AI Engineer":          [7, 12, 18, 28, 48],
            "Full Stack Developer": [4, 7, 12, 19, 32],
            "Cybersecurity Engineer":[6, 9, 15, 24, 40],
            "Product Manager":      [8, 12, 18, 28, 45]
        }

        levels = ["Fresher", "Junior", "Mid", "Senior", "Lead"]
        salaries = salary_data[selected_role]
        exp_index = ["Fresher (0-1 yr)", "Junior (1-3 yrs)",
                     "Mid (3-5 yrs)", "Senior (5-8 yrs)",
                     "Lead (8+ yrs)"].index(experience)

        current_salary = salaries[exp_index]

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Avg Salary (LPA)", f"₹{current_salary} LPA")
        col2.metric("📉 Min", f"₹{int(current_salary * 0.8)} LPA")
        col3.metric("📈 Max", f"₹{int(current_salary * 1.3)} LPA")

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=levels,
            y=salaries,
            mode="lines+markers+text",
            text=[f"₹{s}L" for s in salaries],
            textposition="top center",
            line=dict(color="#7c3aed", width=3),
            marker=dict(size=12, color="#7c3aed"),
            fill="tozeroy",
            fillcolor="rgba(124,58,237,0.15)"
        ))
        fig4.add_trace(go.Scatter(
            x=[levels[exp_index]],
            y=[salaries[exp_index]],
            mode="markers",
            marker=dict(size=18, color="#f59e0b", symbol="star"),
            name="Your Level"
        ))
        fig4.update_layout(
            title=f"{selected_role} Salary Progression",
            height=380,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            yaxis=dict(title="Salary (LPA ₹)"),
            showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")
        st.subheader("🏢 Top Paying Companies")

        companies = ["Google India", "Microsoft", "Amazon",
                     "Flipkart", "Razorpay", "CRED",
                     "Swiggy", "Zomato", "Infosys", "TCS"]
        avg_pay = [45, 42, 40, 35, 32, 30, 28, 27, 18, 16]

        fig5 = px.bar(
            x=avg_pay, y=companies,
            orientation="h",
            title="Average Package (LPA) by Company",
            color=avg_pay,
            color_continuous_scale="Purples",
            labels={"x": "Avg Package (LPA)", "y": "Company"},
            text=avg_pay
        )
        fig5.update_layout(
            height=450,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig5, use_container_width=True)

    with tab3:
        st.subheader("🛠️ Skills Demand Analyzer")

        col1, col2 = st.columns(2)
        with col1:
            your_role = st.text_input("Your Target Role", placeholder="e.g. Data Scientist")
        with col2:
            your_current_skills = st.text_input("Your Current Skills", placeholder="e.g. Python, SQL, Excel")

        if st.button("🔍 Analyze My Skills", type="primary", use_container_width=True):
            if not your_role or not your_current_skills:
                st.error("Please fill both fields!")
                return

            with st.spinner("🤖 AI is analyzing your skills gap..."):
                prompt = f"""
                For a {your_role} role in India in 2025:
                
                The candidate has these skills: {your_current_skills}
                
                Provide a detailed skills analysis in this EXACT format:
                
                MUST_HAVE: skill1, skill2, skill3, skill4, skill5
                GOOD_TO_HAVE: skill1, skill2, skill3, skill4
                MISSING: skill1, skill2, skill3
                MATCH_SCORE: XX
                VERDICT: one sentence verdict
                ROADMAP: step1 | step2 | step3 | step4
                """
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                result = response.choices[0].message.content

            must_have = good_to_have = missing = match = verdict = roadmap = ""
            for line in result.strip().split("\n"):
                if "MUST_HAVE:" in line:
                    must_have = line.split("MUST_HAVE:")[1].strip()
                elif "GOOD_TO_HAVE:" in line:
                    good_to_have = line.split("GOOD_TO_HAVE:")[1].strip()
                elif "MISSING:" in line:
                    missing = line.split("MISSING:")[1].strip()
                elif "MATCH_SCORE:" in line:
                    match = line.split("MATCH_SCORE:")[1].strip()
                elif "VERDICT:" in line:
                    verdict = line.split("VERDICT:")[1].strip()
                elif "ROADMAP:" in line:
                    roadmap = line.split("ROADMAP:")[1].strip()

            st.success("✅ Skills Analysis Complete!")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Skills Match", f"{match}%")
            with col2:
                st.metric("✅ You Have", f"{len(your_current_skills.split(','))} skills")
            with col3:
                missing_count = len(missing.split(",")) if missing else 0
                st.metric("❌ Skills Missing", missing_count)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Must-Have Skills:**")
                for s in must_have.split(","):
                    have = s.strip().lower() in your_current_skills.lower()
                    icon = "✅" if have else "❌"
                    st.markdown(f"{icon} {s.strip()}")

                st.markdown("**⭐ Good to Have:**")
                for s in good_to_have.split(","):
                    st.markdown(f"💡 {s.strip()}")

            with col2:
                match_val = int(match) if match.isdigit() else 50
                fig6 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=match_val,
                    title={"text": "Skills Match %"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#7c3aed"},
                        "steps": [
                            {"range": [0, 40], "color": "#fee2e2"},
                            {"range": [40, 70], "color": "#fef3c7"},
                            {"range": [70, 100], "color": "#d1fae5"}
                        ]
                    }
                ))
                fig6.update_layout(
                    height=280,
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white")
                )
                st.plotly_chart(fig6, use_container_width=True)

            if verdict:
                st.info(f"💬 **Verdict:** {verdict}")

            if roadmap:
                st.markdown("---")
                st.subheader("🗺️ Your Learning Roadmap")
                steps = roadmap.split("|")
                cols = st.columns(len(steps))
                for i, (col, step) in enumerate(zip(cols, steps)):
                    col.markdown(
                        f'<div style="background:#1e1e2e;padding:12px;'
                        f'border-radius:8px;border-top:3px solid #7c3aed;'
                        f'text-align:center;font-size:13px;">'
                        f'<b>Step {i+1}</b><br>{step.strip()}</div>',
                        unsafe_allow_html=True
                    )