import streamlit as st
from database import db_manager
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

def show_auth_page():
    """Show authentication page (login/signup)"""
    
    st.markdown("""
        <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 10px;
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .auth-title {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Center the authentication form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Logo and title
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="color: #4f8cff; margin-bottom: 0.5rem;">🍽️ AI Calories Tracker</h1>
                <p style="color: #666; margin: 0;">Track your nutrition with AI-powered analysis</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Toggle between login and signup
        auth_mode = st.radio("", ["Login", "Sign Up"], horizontal=True)
        
        if auth_mode == "Login":
            show_login_form()
        else:
            show_signup_form()
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_login_form():
    """Show login form"""
    with st.form("login_form"):
        st.markdown("### Welcome Back!")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submit_login = st.form_submit_button("Login", use_container_width=True)
        
        if submit_login:
            if not username or not password:
                st.error("Please fill in all fields")
                return
            
            success, user_data, message = db_manager.authenticate_user(username, password)
            
            if success:
                st.session_state.authenticated = True
                st.session_state.user = user_data
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error(message)

def show_signup_form():
    """Show signup form"""
    with st.form("signup_form"):
        st.markdown("### Create Account")
        
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        st.markdown("#### Gemini API Configuration")
        st.info("💡 You'll need a Gemini API key to analyze your meals. Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)")
        gemini_api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your Gemini API key")
        
        submit_signup = st.form_submit_button("Create Account", use_container_width=True)
        
        if submit_signup:
            # Validation
            if not all([username, email, password, confirm_password, gemini_api_key]):
                st.error("Please fill in all fields")
                return
            
            if not validate_email(email):
                st.error("Please enter a valid email address")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            is_valid, password_message = validate_password(password)
            if not is_valid:
                st.error(password_message)
                return
            
            # Try to create user
            success, message = db_manager.create_user(username, email, password, gemini_api_key)
            
            if success:
                st.success("Account created successfully! You can now login.")
                st.balloons()
            else:
                st.error(message)

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()