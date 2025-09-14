import streamlit as st
import os
from database import db_manager
from auth import show_auth_page, logout
from pages.home import show_home_page
from pages.ai_calculator import show_ai_calculator
from pages.settings import show_settings_page
from pages.goals import show_goals_page

# Page configuration
st.set_page_config(
    page_title="AI Calories Tracker Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Custom CSS for mobile-responsive design and styling
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile-first responsive design */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Bottom navigation bar */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.5rem 0;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        border-radius: 15px 15px 0 0;
    }
    
    .nav-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        max-width: 500px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: white;
        text-decoration: none;
        padding: 0.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
        min-width: 60px;
    }
    
    .nav-item:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-2px);
    }
    
    .nav-item.active {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
    }
    
    .nav-icon {
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }
    
    .nav-text {
        font-size: 0.75rem;
        text-align: center;
        line-height: 1;
    }
    
    /* Main content area with bottom padding for nav */
    .main-content {
        padding-bottom: 100px;
        min-height: calc(100vh - 100px);
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .app-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    /* Card styling */
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #f0f0f0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Responsive breakpoints */
    @media (max-width: 768px) {
        .main-container {
            padding: 0 0.5rem;
        }
        
        .app-header {
            margin: -1rem -0.5rem 2rem -0.5rem;
        }
        
        .nav-text {
            font-size: 0.7rem;
        }
        
        .nav-icon {
            font-size: 1.3rem;
        }
    }
    
    @media (max-width: 480px) {
        .nav-container {
            padding: 0 0.5rem;
        }
        
        .nav-item {
            min-width: 50px;
            padding: 0.3rem;
        }
        
        .nav-text {
            font-size: 0.65rem;
        }
        
        .nav-icon {
            font-size: 1.2rem;
        }
    }
    
    /* Hide scrollbar for cleaner look */
    .main::-webkit-scrollbar {
        display: none;
    }
    
    .main {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

def show_bottom_navigation():
    """Display the bottom navigation bar"""
    current_page = st.session_state.get('current_page', 'home')
    
    nav_items = [
        ('home', '🏠', 'Home'),
        ('ai_calculator', '🤖', 'AI Calc'),
        ('goals', '🎯', 'Goals'),
        ('settings', '⚙️', 'Settings')
    ]
    
    nav_html = '<div class="bottom-nav"><div class="nav-container">'
    
    for page_id, icon, label in nav_items:
        active_class = 'active' if current_page == page_id else ''
        nav_html += f'''
        <div class="nav-item {active_class}" onclick="navigateToPage('{page_id}')">
            <div class="nav-icon">{icon}</div>
            <div class="nav-text">{label}</div>
        </div>
        '''
    
    nav_html += '</div></div>'
    
    # JavaScript for navigation
    nav_html += '''
    <script>
    function navigateToPage(page) {
        // Send page change to Streamlit
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            data: {page: page}
        }, "*");
        
        // Update active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        event.currentTarget.classList.add('active');
    }
    </script>
    '''
    
    return nav_html

def handle_navigation():
    """Handle page navigation based on user interaction"""
    # Create navigation buttons (hidden, just for functionality)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠", key="nav_home", help="Home"):
            st.session_state.current_page = 'home'
            st.rerun()
    
    with col2:
        if st.button("🤖", key="nav_ai", help="AI Calculator"):
            st.session_state.current_page = 'ai_calculator'
            st.rerun()
    
    with col3:
        if st.button("🎯", key="nav_goals", help="Goals"):
            st.session_state.current_page = 'goals'
            st.rerun()
    
    with col4:
        if st.button("⚙️", key="nav_settings", help="Settings"):
            st.session_state.current_page = 'settings'
            st.rerun()

def show_header():
    """Show the app header"""
    user = st.session_state.user
    page_titles = {
        'home': 'Dashboard',
        'ai_calculator': 'AI Calories Calculator',
        'goals': 'Daily Goals',
        'settings': 'Settings'
    }
    
    current_title = page_titles.get(st.session_state.current_page, 'Dashboard')
    
    header_html = f'''
    <div class="app-header">
        <div class="app-title">🍽️ AI Calories Tracker</div>
        <div class="app-subtitle">{current_title}</div>
    </div>
    '''
    
    st.markdown(header_html, unsafe_allow_html=True)

def main():
    """Main application logic"""
    
    # Check authentication
    if not st.session_state.authenticated:
        show_auth_page()
        return
    
    # Initialize database (in a real app, this would be done during setup)
    try:
        if not db_manager.init_database():
            st.error("⚠️ Database connection failed. Using placeholder data for demo.")
            st.info("💡 Please configure your database settings in the .env file.")
    except Exception as e:
        st.error(f"Database error: {e}")
        st.info("💡 Please check your database configuration in the .env file.")
    
    # Show header
    show_header()
    
    # Main content area
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Route to appropriate page
    current_page = st.session_state.current_page
    
    if current_page == 'home':
        show_home_page()
    elif current_page == 'ai_calculator':
        show_ai_calculator()
    elif current_page == 'goals':
        show_goals_page()
    elif current_page == 'settings':
        show_settings_page()
    else:
        show_home_page()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle navigation
    handle_navigation()
    
    # Show bottom navigation
    st.markdown(show_bottom_navigation(), unsafe_allow_html=True)

if __name__ == "__main__":
    main()