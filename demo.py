#!/usr/bin/env python3
"""
Demo script for AI Calories Tracker Dashboard

This script demonstrates the key features without requiring database setup.
Run with: python demo.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import json

def create_demo_data():
    """Create demo nutrition data for testing"""
    demo_data = {
        'user': {
            'id': 1,
            'username': 'demo_user',
            'email': 'demo@example.com',
            'daily_calorie_goal': 2200,
            'daily_protein_goal': 150,
            'daily_carb_goal': 275,
            'daily_fat_goal': 73
        },
        'daily_nutrition': {
            'calories': 1850,
            'protein': 120,
            'carbs': 230,
            'fat': 65,
            'sugar': 45,
            'fiber': 28
        },
        'meals': [
            {
                'type': 'breakfast',
                'time': '08:30',
                'calories': 420,
                'protein': 25,
                'carbs': 45,
                'fat': 18,
                'analysis': 'Healthy breakfast with oats, berries, and Greek yogurt. Good balance of macronutrients.'
            },
            {
                'type': 'lunch',
                'time': '12:45',
                'calories': 650,
                'protein': 35,
                'carbs': 85,
                'fat': 22,
                'analysis': 'Grilled chicken salad with quinoa and avocado. Excellent protein content and healthy fats.'
            },
            {
                'type': 'dinner',
                'time': '19:15',
                'calories': 580,
                'protein': 40,
                'carbs': 75,
                'fat': 18,
                'analysis': 'Salmon with sweet potato and steamed vegetables. Rich in omega-3 fatty acids.'
            },
            {
                'type': 'snack',
                'time': '15:30',
                'calories': 200,
                'protein': 20,
                'carbs': 25,
                'fat': 7,
                'analysis': 'Protein smoothie with banana and almond butter. Great post-workout nutrition.'
            }
        ]
    }
    return demo_data

def show_demo_dashboard():
    """Display the demo dashboard"""
    st.set_page_config(
        page_title="AI Calories Tracker - Demo",
        page_icon="🍽️",
        layout="wide"
    )
    
    # Demo CSS
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .demo-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="demo-header">
        <h1>🍽️ AI Calories Tracker Dashboard - Demo</h1>
        <p>Experience the full nutrition tracking capabilities</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load demo data
    data = create_demo_data()
    user = data['user']
    nutrition = data['daily_nutrition']
    goals = user
    
    # Daily Progress Section
    st.subheader("📊 Today's Progress")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        progress = nutrition['calories'] / goals['daily_calorie_goal']
        st.metric("Calories", f"{int(nutrition['calories'])}", f"of {goals['daily_calorie_goal']} kcal")
        st.progress(min(progress, 1.0))
    
    with col2:
        progress = nutrition['protein'] / goals['daily_protein_goal']
        st.metric("Protein", f"{int(nutrition['protein'])}g", f"of {goals['daily_protein_goal']}g")
        st.progress(min(progress, 1.0))
    
    with col3:
        progress = nutrition['carbs'] / goals['daily_carb_goal']
        st.metric("Carbs", f"{int(nutrition['carbs'])}g", f"of {goals['daily_carb_goal']}g")
        st.progress(min(progress, 1.0))
    
    with col4:
        progress = nutrition['fat'] / goals['daily_fat_goal']
        st.metric("Fat", f"{int(nutrition['fat'])}g", f"of {goals['daily_fat_goal']}g")
        st.progress(min(progress, 1.0))
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥧 Macronutrient Breakdown")
        
        # Calculate calories from macros
        protein_cal = nutrition['protein'] * 4
        carbs_cal = nutrition['carbs'] * 4
        fat_cal = nutrition['fat'] * 9
        
        pie_data = pd.DataFrame({
            'Macronutrient': ['Protein', 'Carbs', 'Fat'],
            'Calories': [protein_cal, carbs_cal, fat_cal]
        })
        
        fig = px.pie(
            pie_data, 
            values='Calories', 
            names='Macronutrient',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Goals vs Actual")
        
        comparison_data = pd.DataFrame({
            'Nutrient': ['Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)'],
            'Goal': [goals['daily_calorie_goal'], goals['daily_protein_goal'], 
                    goals['daily_carb_goal'], goals['daily_fat_goal']],
            'Actual': [nutrition['calories'], nutrition['protein'], 
                      nutrition['carbs'], nutrition['fat']]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Goal',
            x=comparison_data['Nutrient'],
            y=comparison_data['Goal'],
            marker_color='lightblue',
            opacity=0.7
        ))
        fig.add_trace(go.Bar(
            name='Actual',
            x=comparison_data['Nutrient'],
            y=comparison_data['Actual'],
            marker_color='darkblue'
        ))
        
        fig.update_layout(barmode='group', title="Goals vs Actual Intake")
        st.plotly_chart(fig, use_container_width=True)
    
    # Meals section
    st.subheader("🍽️ Today's Meals")
    
    for meal in data['meals']:
        with st.expander(f"{meal['type'].title()} - {meal['time']} ({int(meal['calories'])} kcal)"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write(f"**Calories:** {int(meal['calories'])} kcal")
                st.write(f"**Protein:** {meal['protein']}g")
                st.write(f"**Carbs:** {meal['carbs']}g")
                st.write(f"**Fat:** {meal['fat']}g")
            
            with col2:
                st.markdown("**AI Analysis:**")
                st.write(meal['analysis'])
    
    # Weekly trend
    st.subheader("📈 Weekly Calorie Trend")
    
    # Generate sample weekly data
    weekly_data = []
    for i in range(7):
        day = date.today() - timedelta(days=6-i)
        calories = 1800 + (i * 100) + (50 if i % 2 == 0 else -50)  # Simulate variation
        weekly_data.append({'Date': day, 'Calories': calories})
    
    weekly_df = pd.DataFrame(weekly_data)
    
    fig = px.line(
        weekly_df, 
        x='Date', 
        y='Calories',
        title="7-Day Calorie Trend",
        markers=True
    )
    fig.add_hline(y=goals['daily_calorie_goal'], line_dash="dash", 
                 line_color="red", annotation_text="Daily Goal")
    st.plotly_chart(fig, use_container_width=True)
    
    # Features showcase
    st.markdown("---")
    st.subheader("✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🤖 AI Analysis**
        - Gemini 2.5 Flash model
        - Food image recognition
        - Nutrition calculation
        - Portion size estimation
        """)
    
    with col2:
        st.markdown("""
        **📊 Dashboard**
        - Real-time progress tracking
        - Interactive charts
        - Goal monitoring
        - Weekly trends
        """)
    
    with col3:
        st.markdown("""
        **📱 Mobile Ready**
        - Responsive design
        - Touch-friendly interface
        - Bottom navigation
        - Offline capabilities
        """)
    
    # Call to action
    st.markdown("---")
    st.markdown("""
    <div class="demo-header">
        <h3>Ready to track your nutrition?</h3>
        <p>Set up your database and run: <code>streamlit run app.py</code></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_demo_dashboard()