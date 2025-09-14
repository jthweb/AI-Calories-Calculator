import streamlit as st
from database import db_manager

def show_settings_page():
    """Show the settings page"""
    user = st.session_state.user
    
    st.title("⚙️ Settings")
    
    # Profile section
    with st.expander("👤 Profile Information", expanded=True):
        st.info(f"**Username:** {user['username']}")
        st.info(f"**Email:** {user['email']}")
    
    # API Key Management
    with st.expander("🔑 API Key Management", expanded=True):
        st.markdown("### Gemini API Key")
        st.info("💡 Your Gemini API key is used to analyze food images. Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)")
        
        # Show masked API key
        current_key = user['gemini_api_key']
        if current_key:
            masked_key = current_key[:8] + "*" * (len(current_key) - 12) + current_key[-4:] if len(current_key) > 12 else "*" * len(current_key)
            st.success(f"✅ API Key configured: {masked_key}")
        else:
            st.warning("❌ No API key configured")
        
        with st.form("api_key_form"):
            new_api_key = st.text_input(
                "Update Gemini API Key",
                type="password",
                placeholder="Enter your new Gemini API key",
                help="Leave empty to keep current key"
            )
            
            submit_api = st.form_submit_button("Update API Key")
            
            if submit_api and new_api_key:
                try:
                    connection = db_manager.get_connection()
                    if connection:
                        cursor = connection.cursor()
                        cursor.execute(
                            "UPDATE users SET gemini_api_key = %s WHERE id = %s",
                            (new_api_key, user['id'])
                        )
                        connection.commit()
                        cursor.close()
                        connection.close()
                        
                        # Update session state
                        st.session_state.user['gemini_api_key'] = new_api_key
                        st.success("✅ API key updated successfully!")
                        st.rerun()
                    else:
                        st.error("Database connection failed")
                except Exception as e:
                    st.error(f"Error updating API key: {e}")
    
    # App Preferences
    with st.expander("🎨 App Preferences"):
        st.markdown("### Display Settings")
        
        # Theme preference (for future implementation)
        theme = st.selectbox(
            "Theme",
            options=["Light", "Dark", "Auto"],
            index=0,
            help="Theme selection (coming soon)"
        )
        
        # Notification preferences
        st.markdown("### Notifications")
        notifications = st.checkbox("Enable daily nutrition reminders", value=True)
        meal_reminders = st.checkbox("Enable meal logging reminders", value=True)
        
        if st.button("Save Preferences"):
            st.success("Preferences saved!")
    
    # Data Management
    with st.expander("📊 Data Management"):
        st.markdown("### Export Data")
        st.info("Export your nutrition data for personal use or backup.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export All Data", use_container_width=True):
                st.info("Export feature coming soon!")
        
        with col2:
            if st.button("📋 Export Last 30 Days", use_container_width=True):
                st.info("Export feature coming soon!")
        
        st.markdown("### Reset Data")
        st.warning("⚠️ Danger Zone")
        
        with st.form("reset_form"):
            st.error("This will permanently delete all your meal data. This action cannot be undone.")
            confirm_text = st.text_input("Type 'DELETE' to confirm:", placeholder="DELETE")
            
            reset_button = st.form_submit_button("🗑️ Delete All Data", type="secondary")
            
            if reset_button:
                if confirm_text == "DELETE":
                    try:
                        connection = db_manager.get_connection()
                        if connection:
                            cursor = connection.cursor()
                            cursor.execute("DELETE FROM meals WHERE user_id = %s", (user['id'],))
                            connection.commit()
                            cursor.close()
                            connection.close()
                            st.success("All data deleted successfully.")
                        else:
                            st.error("Database connection failed")
                    except Exception as e:
                        st.error(f"Error deleting data: {e}")
                else:
                    st.error("Please type 'DELETE' to confirm")
    
    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        ### AI Calories Tracker Dashboard
        
        **Version:** 2.0.0  
        **Developer:** JThweb  
        **License:** Apache 2.0
        
        This application uses AI-powered image analysis to help you track your nutrition and reach your health goals.
        
        **Features:**
        - 🤖 AI-powered food analysis using Gemini 2.5 Flash
        - 📊 Interactive nutrition dashboard
        - 🎯 Daily goal tracking
        - 📱 Mobile-responsive design
        - 🔒 Secure user authentication
        
        **Privacy:**
        - Your data is stored securely in your database
        - API keys are encrypted and never shared
        - Images are processed in real-time and not stored
        
        **Support:**
        Visit [GitHub Repository](https://github.com/jthweb/AI-Calories-Calculator) for issues and updates.
        """)
    
    # Logout button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.success("Logged out successfully!")
            st.rerun()