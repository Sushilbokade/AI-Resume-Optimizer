import streamlit as st
import requests
import json
import os
from typing import Dict, List, Optional
import io
import base64
from datetime import datetime
import time

# Import custom components
try:
    from components.dashboard import render_dashboard
    from components.upload import render_upload_page
    from components.job_match import render_job_match_page
    from components.export import render_export_page
except ImportError:
    # Fallback if components are not available
    pass

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def main():
    """Main application entry point"""

    # Configure Streamlit page
    st.set_page_config(
        page_title="AI Resume Pro",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    initialize_session_state()

    # Custom CSS
    load_custom_css()

    # Check authentication
    if not st.session_state.get("authenticated", False):
        render_auth_page()
    else:
        render_main_app()

def initialize_session_state():
    """Initialize session state variables"""

    default_states = {
        "authenticated": False,
        "user_info": None,
        "access_token": None,
        "openai_api_key": None,
        "has_openai_key": False,
        "current_page": "Dashboard",
        "uploaded_resume": None,
        "parsed_resume": None,
        "job_descriptions": [],
        "current_job": None,
        "ai_suggestions": [],
        "match_analysis": None,
        "export_history": []
    }

    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_custom_css():
    """Load custom CSS styling"""

    st.markdown("""
    <style>
        /* Main container styling */
        .main-container {
            padding: 1rem;
        }

        /* Card styling */
        .info-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin: 0.5rem 0;
        }

        /* Button styling */
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f8f9fa;
        }

        /* Upload area styling */
        .upload-area {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background-color: #f8f9fa;
        }

        /* Success/Error message styling */
        .success-message {
            color: #28a745;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 0.75rem;
            border-radius: 5px;
            margin: 1rem 0;
        }

        .error-message {
            color: #dc3545;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 0.75rem;
            border-radius: 5px;
            margin: 1rem 0;
        }

        /* Suggestion cards */
        .suggestion-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .suggestion-accepted {
            border-left: 4px solid #28a745;
        }

        .suggestion-rejected {
            border-left: 4px solid #dc3545;
        }

        /* Score indicators */
        .score-excellent { color: #28a745; font-weight: bold; }
        .score-good { color: #ffc107; font-weight: bold; }
        .score-poor { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def render_auth_page():
    """Render authentication page"""

    st.markdown("""
    <div class="info-card">
        <h1>🚀 Welcome to AI Resume Pro</h1>
        <p>Transform your resume with AI-powered customization for every job application</p>
    </div>
    """, unsafe_allow_html=True)

    # Create tabs for login and register
    auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])

    with auth_tab1:
        render_login_form()

    with auth_tab2:
        render_register_form()

def render_login_form():
    """Render login form"""

    st.subheader("Login to Your Account")

    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        col1, col2 = st.columns(2)

        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)

        with col2:
            demo_button = st.form_submit_button("Demo Login", use_container_width=True)

    if login_button:
        if email and password:
            with st.spinner("Logging in..."):
                success = login_user(email, password)
                if success:
                    st.success("Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
        else:
            st.error("Please fill in all fields.")

    if demo_button:
        # Demo login with mock data
        st.session_state.authenticated = True
        st.session_state.user_info = {
            "name": "Demo User",
            "email": "demo@example.com",
            "id": "demo-user-id"
        }
        st.session_state.access_token = "demo-token"
        st.success("Demo login successful!")
        time.sleep(1)
        st.rerun()

def render_register_form():
    """Render registration form"""

    st.subheader("Create New Account")

    with st.form("register_form"):
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")

        register_button = st.form_submit_button("Create Account", use_container_width=True)

    if register_button:
        if all([name, email, password, confirm_password, agree_terms]):
            if password == confirm_password:
                with st.spinner("Creating account..."):
                    success = register_user(name, email, password)
                    if success:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Registration failed. Please try again.")
            else:
                st.error("Passwords do not match.")
        else:
            st.error("Please fill in all fields and agree to the terms.")

def render_main_app():
    """Render main application interface"""

    # Sidebar navigation
    render_sidebar()

    # Main content area
    if st.session_state.current_page == "Dashboard":
        render_dashboard_page()
    elif st.session_state.current_page == "Upload Resume":
        render_upload_resume_page()
    elif st.session_state.current_page == "Job Match":
        render_job_match_page()
    elif st.session_state.current_page == "Export":
        render_export_page_content()
    elif st.session_state.current_page == "Settings":
        render_settings_page()

def render_sidebar():
    """Render sidebar navigation"""

    with st.sidebar:
        # User info
        user_info = st.session_state.get("user_info", {})
        st.markdown(f"""
        <div class="info-card">
            <h3>👋 Welcome back!</h3>
            <p><strong>{user_info.get('name', 'User')}</strong></p>
            <p>{user_info.get('email', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation menu
        st.markdown("### Navigation")

        pages = [
            ("Dashboard", "📊"),
            ("Upload Resume", "📤"),
            ("Job Match", "🎯"),  
            ("Export", "📥"),
            ("Settings", "⚙️")
        ]

        for page_name, icon in pages:
            if st.button(f"{icon} {page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()

        st.markdown("---")

        # Quick stats
        st.markdown("### Quick Stats")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Resumes", 3)
        with col2:
            st.metric("Success Rate", "85%")

        st.markdown("---")

        # OpenAI API Key Status
        render_api_key_status()

        st.markdown("---")

        # Logout button
        if st.button("Logout", use_container_width=True):
            logout_user()

def render_api_key_status():
    """Render OpenAI API key status and input"""

    st.markdown("### OpenAI API Key")

    has_key = st.session_state.get("has_openai_key", False)

    if has_key:
        st.success("✅ API Key Configured")
        if st.button("Update API Key", use_container_width=True):
            st.session_state.show_api_key_input = True
    else:
        st.warning("⚠️ API Key Required")
        st.info("You need to provide your OpenAI API key to use AI features.")

        if st.button("Add API Key", use_container_width=True):
            st.session_state.show_api_key_input = True

    # API Key input form
    if st.session_state.get("show_api_key_input", False):
        with st.form("api_key_form"):
            api_key = st.text_input(
                "OpenAI API Key", 
                type="password",
                placeholder="sk-...",
                help="Get your API key from https://platform.openai.com/api-keys"
            )

            col1, col2 = st.columns(2)
            with col1:
                save_key = st.form_submit_button("Save Key")
            with col2:
                cancel = st.form_submit_button("Cancel")

        if save_key and api_key:
            with st.spinner("Validating API key..."):
                # In demo mode, just accept any key that looks valid
                if api_key.startswith("sk-") and len(api_key) > 20:
                    st.success("API key saved successfully!")
                    st.session_state.has_openai_key = True
                    st.session_state.openai_api_key = api_key
                    st.session_state.show_api_key_input = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid API key format. Please check and try again.")

        if cancel:
            st.session_state.show_api_key_input = False
            st.rerun()

def render_dashboard_page():
    """Render dashboard page"""

    st.title("📊 Dashboard")

    # Welcome section
    user_info = st.session_state.get("user_info", {})
    user_name = user_info.get("name", "User")

    st.markdown(f"""
    <div class="info-card">
        <h2>Welcome back, {user_name}! 👋</h2>
        <p>Here's your resume customization overview</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📄 Total Resumes", "12", "+2")
    with col2:
        st.metric("📈 Success Rate", "78%", "+5%")
    with col3:
        st.metric("🎯 Recent Matches", "5", "This month")
    with col4:
        st.metric("⭐ Avg Score", "85", "Excellent")

    # Recent activity
    st.subheader("📝 Recent Resume Versions")

    recent_resumes = [
        {"title": "Software Engineer - Google", "date": "2024-08-01", "score": 92, "status": "Exported"},
        {"title": "Full Stack Developer - Microsoft", "date": "2024-07-28", "score": 88, "status": "Draft"},
        {"title": "Senior Developer - Amazon", "date": "2024-07-25", "score": 85, "status": "Exported"}
    ]

    for resume in recent_resumes:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{resume['title']}**")
            st.write(f"*{resume['date']}*")
        with col2:
            st.write(f"**{resume['score']}%**")
        with col3:
            status_color = "🟢" if resume['status'] == "Exported" else "🟡"
            st.write(f"{status_color} {resume['status']}")
        st.divider()

def render_upload_resume_page():
    """Render resume upload page"""

    st.title("📤 Upload Master Resume")

    # Check API key status
    if not st.session_state.get("has_openai_key", False):
        st.warning("⚠️ Please configure your OpenAI API key in the sidebar to enable AI features.")

    st.markdown("""
    <div class="upload-area">
        <h3>📁 Upload Your Resume</h3>
        <p>Support formats: PDF, DOCX, DOC (Max 10MB)</p>
    </div>
    """, unsafe_allow_html=True)

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx', 'doc'],
        help="Upload your master resume that will be customized for different job applications"
    )

    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size / 1024:.1f} KB")
            st.write(f"**File type:** {uploaded_file.type}")

        # Process button
        with col2:
            if st.button("🔄 Process Resume", use_container_width=True, type="primary"):
                process_uploaded_resume(uploaded_file)

def process_uploaded_resume(uploaded_file):
    """Process the uploaded resume file"""

    with st.spinner("Processing your resume..."):

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Upload file
        status_text.text("Uploading file...")
        progress_bar.progress(20)
        time.sleep(1)

        # Step 2: Parse content
        status_text.text("Parsing resume content...")
        progress_bar.progress(50)

        # Mock parsing (in real app, this would call the API)
        parsed_data = {
            "personal_info": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1 (555) 123-4567",
                "location": "San Francisco, CA"
            },
            "summary": "Experienced software engineer with 5+ years developing scalable web applications.",
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp Inc.",
                    "start_date": "2022-01-01",
                    "end_date": "Present",
                    "bullets": [
                        "Led development of microservices architecture serving 1M+ users",
                        "Implemented CI/CD pipelines reducing deployment time by 60%"
                    ]
                }
            ],
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
            "education": [
                {
                    "degree": "B.S. Computer Science",
                    "school": "University of California, Berkeley",
                    "graduation_year": "2019"
                }
            ]
        }

        progress_bar.progress(80)

        # Step 3: Extract sections
        status_text.text("Extracting sections and formatting...")
        time.sleep(1)
        progress_bar.progress(100)

        st.session_state.uploaded_resume = uploaded_file
        st.session_state.parsed_resume = parsed_data

        status_text.text("✅ Resume processed successfully!")
        time.sleep(1)

        # Show results
        render_parsing_results()

def render_parsing_results():
    """Render parsing results and extracted content"""

    st.markdown("---")
    st.subheader("📋 Parsing Results")

    parsed_data = st.session_state.get("parsed_resume")

    if parsed_data:
        st.success("✅ Resume parsed successfully!")

        # Show parsed sections in tabs
        tabs = st.tabs(["Personal Info", "Summary", "Experience", "Skills", "Education"])

        with tabs[0]:
            render_personal_info_section(parsed_data.get("personal_info", {}))

        with tabs[1]:
            st.write(parsed_data.get("summary", "No summary found"))

        with tabs[2]:
            render_experience_section(parsed_data.get("experience", []))

        with tabs[3]:
            render_skills_section(parsed_data.get("skills", []))

        with tabs[4]:
            render_education_section(parsed_data.get("education", []))

        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save as Master Resume", use_container_width=True):
                st.success("✅ Master resume saved successfully!")

        with col2:
            if st.button("✏️ Edit Content", use_container_width=True):
                st.info("Edit functionality would be implemented here")

        with col3:
            if st.button("🎯 Match with Job", use_container_width=True):
                st.session_state.current_page = "Job Match"
                st.rerun()

def render_personal_info_section(personal_info: dict):
    """Render personal information section"""

    if not personal_info:
        st.info("No personal information extracted.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Name:**", personal_info.get("name", "Not found"))
        st.write("**Email:**", personal_info.get("email", "Not found"))
        st.write("**Phone:**", personal_info.get("phone", "Not found"))

    with col2:
        st.write("**Location:**", personal_info.get("location", "Not found"))
        st.write("**LinkedIn:**", personal_info.get("linkedin", "Not found"))
        st.write("**GitHub:**", personal_info.get("github", "Not found"))

def render_experience_section(experience: list):
    """Render experience section"""

    if not experience:
        st.info("No work experience found.")
        return

    for i, exp in enumerate(experience, 1):
        with st.expander(f"Position {i}: {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Title:**", exp.get("title", ""))
                st.write("**Company:**", exp.get("company", ""))

            with col2:
                st.write("**Duration:**", f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}")
                st.write("**Location:**", exp.get("location", ""))

            if exp.get("bullets"):
                st.write("**Key Responsibilities:**")
                for bullet in exp["bullets"]:
                    st.write(f"• {bullet}")

def render_skills_section(skills: list):
    """Render skills section"""

    if skills:
        # Display skills as tags
        skills_html = ""
        for skill in skills:
            skills_html += f'<span style="background: #667eea; color: white; padding: 0.25rem 0.5rem; margin: 0.25rem; border-radius: 15px; display: inline-block; font-size: 0.9em;">{skill}</span>'

        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.info("No skills found.")

def render_education_section(education: list):
    """Render education section"""

    if not education:
        st.info("No education information found.")
        return

    for i, edu in enumerate(education, 1):
        with st.expander(f"Education {i}: {edu.get('degree', 'Unknown')}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Degree:**", edu.get("degree", ""))
                st.write("**School:**", edu.get("school", ""))

            with col2:
                st.write("**Year:**", edu.get("graduation_year", ""))
                st.write("**GPA:**", edu.get("gpa", ""))

def render_job_match_page():
    """Render job matching page"""

    st.title("🎯 Job Match & AI Enhancement")

    if not st.session_state.get("has_openai_key", False):
        st.error("⚠️ OpenAI API key required for AI features. Please add your API key in the sidebar.")
        return

    # Job description input
    st.subheader("📋 Job Description Analysis")

    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title", placeholder="Senior Software Engineer")
        company = st.text_input("Company", placeholder="Google")

    with col2:
        job_url = st.text_input("Job URL (optional)", placeholder="https://...")

    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the full job description here..."
    )

    if st.button("🔍 Analyze Job Description", type="primary"):
        if job_title and company and job_description:
            with st.spinner("Analyzing job description..."):
                # Mock analysis
                time.sleep(2)

                analysis = {
                    "required_skills": ["Python", "React", "AWS", "Docker", "Kubernetes"],
                    "experience_level": "Senior",
                    "key_responsibilities": [
                        "Design scalable systems",
                        "Lead technical projects",
                        "Mentor junior developers"
                    ]
                }

                st.session_state.current_job = {
                    "title": job_title,
                    "company": company,
                    "description": job_description,
                    "analysis": analysis
                }

                st.success("✅ Job description analyzed successfully!")

                # Show analysis results
                render_job_analysis_results(analysis)
        else:
            st.error("Please fill in all required fields.")

    # If we have a current job, show matching interface
    if st.session_state.get("current_job"):
        st.markdown("---")
        render_resume_matching_interface()

def render_job_analysis_results(analysis):
    """Render job analysis results"""

    st.subheader("📊 Analysis Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Required Skills:**")
        for skill in analysis["required_skills"]:
            st.write(f"• {skill}")

    with col2:
        st.write("**Experience Level:**")
        st.write(analysis["experience_level"])

    with col3:
        st.write("**Key Responsibilities:**")
        for resp in analysis["key_responsibilities"][:3]:
            st.write(f"• {resp}")

def render_resume_matching_interface():
    """Render resume matching and AI suggestions interface"""

    st.subheader("🤖 AI Resume Enhancement")

    if not st.session_state.get("parsed_resume"):
        st.warning("Please upload and parse a resume first.")
        return

    if st.button("🚀 Generate AI Suggestions", type="primary"):
        with st.spinner("Generating AI suggestions..."):
            time.sleep(3)

            # Mock AI suggestions
            suggestions = [
                {
                    "section": "experience",
                    "original": "Led development of microservices architecture serving 1M+ users",
                    "suggested": "Architected and led development of scalable microservices infrastructure supporting over 1 million active users with 99.9% uptime, utilizing Docker and Kubernetes",
                    "reason": "Enhanced with specific technologies and reliability metrics",
                    "score": 95
                },
                {
                    "section": "skills", 
                    "original": "Python, JavaScript, React, Node.js, AWS",
                    "suggested": "Python, JavaScript, React, Node.js, AWS (EC2, Lambda, S3), Docker, Kubernetes, Microservices Architecture",
                    "reason": "Added specific AWS services and container technologies to match job requirements",
                    "score": 90
                }
            ]

            st.session_state.ai_suggestions = suggestions
            st.success("✅ AI suggestions generated!")

    # Show AI suggestions if available
    if st.session_state.get("ai_suggestions"):
        render_ai_suggestions()

def render_ai_suggestions():
    """Render AI suggestions with accept/reject interface"""

    st.subheader("💡 AI Suggestions")

    suggestions = st.session_state.get("ai_suggestions", [])

    for i, suggestion in enumerate(suggestions):
        with st.expander(f"Suggestion {i+1}: {suggestion['section'].title()} (Score: {suggestion['score']}%)"):

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Original:**")
                st.write(suggestion["original"])

            with col2:
                st.write("**AI Suggestion:**")
                st.write(suggestion["suggested"])

            st.write("**Reason:**", suggestion["reason"])

            # Accept/Reject buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✅ Accept", key=f"accept_{i}"):
                    st.success("Suggestion accepted!")

            with col2:
                if st.button("❌ Reject", key=f"reject_{i}"):
                    st.info("Suggestion rejected.")

            with col3:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.info("Edit functionality would open here.")

def render_export_page_content():
    """Render export page"""

    st.title("📥 Export Resume")

    if not st.session_state.get("parsed_resume"):
        st.warning("Please upload and process a resume first.")
        return

    st.subheader("📄 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        export_format = st.selectbox(
            "Export Format",
            ["PDF", "DOCX"],
            help="Choose the format for your customized resume"
        )

    with col2:
        template = st.selectbox(
            "Template",
            ["Professional Classic", "Modern Minimal", "Creative Edge"],
            help="Select a resume template"
        )

    filename = st.text_input(
        "Filename",
        value="my_customized_resume",
        help="Enter filename without extension"
    )

    if st.button("📄 Generate Resume", type="primary", use_container_width=True):
        with st.spinner(f"Generating {export_format} resume..."):
            time.sleep(2)

            # Mock file generation
            final_filename = f"{filename}.{export_format.lower()}"

            st.success(f"✅ Resume generated successfully: {final_filename}")

            # Show download button
            st.download_button(
                label=f"⬇️ Download {final_filename}",
                data=b"Mock resume content",  # In real app, this would be the actual file
                file_name=final_filename,
                mime="application/pdf" if export_format == "PDF" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # Export history
    st.markdown("---")
    st.subheader("📚 Export History")

    history = [
        {"filename": "Google_SWE_v3.pdf", "date": "2024-08-01", "format": "PDF"},
        {"filename": "Microsoft_Dev_v2.docx", "date": "2024-07-28", "format": "DOCX"},
        {"filename": "Amazon_Senior_v1.pdf", "date": "2024-07-25", "format": "PDF"}
    ]

    for item in history:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"📄 {item['filename']}")
        with col2:
            st.write(item['date'])
        with col3:
            st.write(item['format'])

def render_settings_page():
    """Render settings page"""

    st.title("⚙️ Settings")

    # User Profile Settings
    st.subheader("Profile Settings")

    user_info = st.session_state.get("user_info", {})

    with st.form("profile_form"):
        name = st.text_input("Full Name", value=user_info.get("name", ""))
        email = st.text_input("Email", value=user_info.get("email", ""), disabled=True)

        if st.form_submit_button("Update Profile"):
            st.success("Profile updated successfully!")

    st.markdown("---")

    # AI Settings
    st.subheader("AI Configuration")

    col1, col2 = st.columns(2)

    with col1:
        model_choice = st.selectbox(
            "OpenAI Model",
            ["gpt-4.1-preview", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0
        )

    with col2:
        max_suggestions = st.slider("Max AI Suggestions", 1, 10, 5)

    creativity_level = st.slider(
        "AI Creativity Level", 
        0.0, 1.0, 0.7,
        help="Higher values make suggestions more creative but less conservative"
    )

    st.markdown("---")

    # Export Settings
    st.subheader("Export Preferences")

    default_format = st.selectbox("Default Export Format", ["PDF", "DOCX"])
    auto_naming = st.checkbox("Automatic File Naming", value=True)

    if auto_naming:
        naming_pattern = st.text_input(
            "Naming Pattern", 
            value="{name}_{job_title}_{date}",
            help="Available variables: {name}, {job_title}, {company}, {date}"
        )

# API Integration Functions (Mock implementations for demo)

def login_user(email: str, password: str) -> bool:
    """Login user via API (mock implementation)"""
    # In demo mode, accept any valid-looking credentials
    if "@" in email and len(password) >= 6:
        st.session_state.authenticated = True
        st.session_state.user_info = {
            "name": email.split("@")[0].title(),
            "email": email,
            "id": "user-123"
        }
        st.session_state.access_token = "mock-token"
        return True
    return False

def register_user(name: str, email: str, password: str) -> bool:
    """Register new user via API (mock implementation)"""
    # In demo mode, always succeed
    return True

def logout_user():
    """Logout user and clear session"""

    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Reinitialize
    initialize_session_state()
    st.rerun()

if __name__ == "__main__":
    main()
