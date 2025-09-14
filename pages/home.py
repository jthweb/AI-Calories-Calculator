import streamlit as st
from database import db_manager
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def show_home_page():
    """Display the main dashboard home page"""
    user = st.session_state.user
    
    st.title(f"Welcome back, {user['username']}! 👋")
    
    # Date selector
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_date = st.date_input("Select Date", value=date.today(), max_value=date.today())
    
    with col2:
        if st.button("Today", use_container_width=True):
            selected_date = date.today()
            st.rerun()
    
    # Get daily nutrition data
    daily_nutrition = db_manager.get_daily_nutrition(user['id'], selected_date)
    
    if daily_nutrition is None:
        daily_nutrition = {
            'calories': 0, 'protein': 0, 'carbs': 0, 
            'fat': 0, 'sugar': 0, 'fiber': 0
        }
    
    # User's daily goals
    goals = {
        'calories': user['daily_calorie_goal'],
        'protein': user['daily_protein_goal'],
        'carbs': user['daily_carb_goal'],
        'fat': user['daily_fat_goal']
    }
    
    # Progress cards
    st.subheader("📊 Daily Progress")
    
    # Calories progress
    calories_progress = min(daily_nutrition['calories'] / goals['calories'], 1.0) if goals['calories'] > 0 else 0
    calories_color = "green" if calories_progress <= 1.0 else "red"
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Calories",
            f"{int(daily_nutrition['calories'])}",
            f"of {goals['calories']} kcal"
        )
        st.progress(calories_progress)
    
    with col2:
        protein_progress = min(daily_nutrition['protein'] / goals['protein'], 1.0) if goals['protein'] > 0 else 0
        st.metric(
            "Protein",
            f"{int(daily_nutrition['protein'])}g",
            f"of {goals['protein']}g"
        )
        st.progress(protein_progress)
    
    with col3:
        carbs_progress = min(daily_nutrition['carbs'] / goals['carbs'], 1.0) if goals['carbs'] > 0 else 0
        st.metric(
            "Carbs",
            f"{int(daily_nutrition['carbs'])}g",
            f"of {goals['carbs']}g"
        )
        st.progress(carbs_progress)
    
    with col4:
        fat_progress = min(daily_nutrition['fat'] / goals['fat'], 1.0) if goals['fat'] > 0 else 0
        st.metric(
            "Fat",
            f"{int(daily_nutrition['fat'])}g",
            f"of {goals['fat']}g"
        )
        st.progress(fat_progress)
    
    # Macronutrient pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        if daily_nutrition['calories'] > 0:
            st.subheader("🥧 Macronutrient Breakdown")
            
            # Calculate calories from each macronutrient
            protein_calories = daily_nutrition['protein'] * 4
            carbs_calories = daily_nutrition['carbs'] * 4
            fat_calories = daily_nutrition['fat'] * 9
            
            if protein_calories + carbs_calories + fat_calories > 0:
                pie_data = pd.DataFrame({
                    'Macronutrient': ['Protein', 'Carbs', 'Fat'],
                    'Calories': [protein_calories, carbs_calories, fat_calories],
                    'Percentage': [
                        protein_calories / (protein_calories + carbs_calories + fat_calories) * 100,
                        carbs_calories / (protein_calories + carbs_calories + fat_calories) * 100,
                        fat_calories / (protein_calories + carbs_calories + fat_calories) * 100
                    ]
                })
                
                fig = px.pie(
                    pie_data, 
                    values='Calories', 
                    names='Macronutrient',
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'],
                    title="Calories by Macronutrient"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No nutrition data for this date")
        else:
            st.info("No meals logged for this date. Start by adding a meal!")
    
    with col2:
        # Goals vs actual chart
        st.subheader("🎯 Goals vs Actual")
        
        comparison_data = pd.DataFrame({
            'Nutrient': ['Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)'],
            'Goal': [goals['calories'], goals['protein'], goals['carbs'], goals['fat']],
            'Actual': [
                daily_nutrition['calories'], 
                daily_nutrition['protein'], 
                daily_nutrition['carbs'], 
                daily_nutrition['fat']
            ]
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
        
        fig.update_layout(
            barmode='group',
            title="Daily Goals vs Actual Intake",
            xaxis_title="Nutrients",
            yaxis_title="Amount"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent meals
    st.subheader("🍽️ Today's Meals")
    meals = db_manager.get_meals_by_date(user['id'], selected_date)
    
    if meals:
        for meal in meals:
            with st.expander(f"{meal['type'].title()} - {meal['time'].strftime('%I:%M %p')} ({int(meal['calories'])} kcal)"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write(f"**Calories:** {int(meal['calories'])} kcal")
                    st.write(f"**Protein:** {meal['protein']:.1f}g")
                    st.write(f"**Carbs:** {meal['carbs']:.1f}g")
                    st.write(f"**Fat:** {meal['fat']:.1f}g")
                
                with col2:
                    if meal['analysis']:
                        st.markdown("**AI Analysis:**")
                        st.write(meal['analysis'])
    else:
        st.info("No meals logged for this date. Use the AI Calculator to add your first meal!")
    
    # Weekly trend (if we have data for multiple days)
    st.subheader("📈 Weekly Calorie Trend")
    
    # Get data for the past 7 days
    weekly_data = []
    for i in range(7):
        day = selected_date - timedelta(days=i)
        day_nutrition = db_manager.get_daily_nutrition(user['id'], day)
        weekly_data.append({
            'Date': day,
            'Calories': day_nutrition['calories'] if day_nutrition else 0
        })
    
    weekly_df = pd.DataFrame(weekly_data)
    weekly_df = weekly_df.sort_values('Date')
    
    if weekly_df['Calories'].sum() > 0:
        fig = px.line(
            weekly_df, 
            x='Date', 
            y='Calories',
            title="7-Day Calorie Trend",
            markers=True
        )
        fig.add_hline(y=goals['calories'], line_dash="dash", line_color="red", 
                     annotation_text="Daily Goal")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to show weekly trend. Keep logging meals to see your progress!")