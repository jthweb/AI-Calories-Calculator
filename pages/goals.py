import streamlit as st
from database import db_manager
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta

def show_goals_page():
    """Show the daily goals and progress tracking page"""
    user = st.session_state.user
    
    st.title("🎯 Daily Goals & Progress")
    
    # Current goals display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Current Daily Goals")
        
        # Display current goals in a nice format
        goals_col1, goals_col2, goals_col3, goals_col4 = st.columns(4)
        
        with goals_col1:
            st.metric("🔥 Calories", f"{user['daily_calorie_goal']}", "kcal")
        
        with goals_col2:
            st.metric("💪 Protein", f"{user['daily_protein_goal']}", "grams")
        
        with goals_col3:
            st.metric("🌾 Carbs", f"{user['daily_carb_goal']}", "grams")
        
        with goals_col4:
            st.metric("🥑 Fat", f"{user['daily_fat_goal']}", "grams")
    
    with col2:
        st.subheader("⚙️ Update Goals")
        if st.button("✏️ Edit Goals", use_container_width=True, type="primary"):
            st.session_state.editing_goals = True
    
    # Goal editing form
    if st.session_state.get('editing_goals', False):
        st.markdown("---")
        st.subheader("✏️ Update Your Daily Goals")
        
        with st.form("goals_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_calories = st.number_input(
                    "Daily Calorie Goal",
                    min_value=1000,
                    max_value=5000,
                    value=user['daily_calorie_goal'],
                    step=50,
                    help="Recommended: 1800-2500 kcal depending on age, gender, and activity level"
                )
                
                new_carbs = st.number_input(
                    "Daily Carbs Goal (g)",
                    min_value=50,
                    max_value=500,
                    value=user['daily_carb_goal'],
                    step=5,
                    help="Recommended: 45-65% of total calories (225-325g for 2000 kcal diet)"
                )
            
            with col2:
                new_protein = st.number_input(
                    "Daily Protein Goal (g)",
                    min_value=50,
                    max_value=300,
                    value=user['daily_protein_goal'],
                    step=5,
                    help="Recommended: 0.8-1.2g per kg of body weight"
                )
                
                new_fat = st.number_input(
                    "Daily Fat Goal (g)",
                    min_value=30,
                    max_value=200,
                    value=user['daily_fat_goal'],
                    step=5,
                    help="Recommended: 20-35% of total calories (44-78g for 2000 kcal diet)"
                )
            
            # Goal preset options
            st.markdown("#### 🎯 Quick Presets")
            preset_col1, preset_col2, preset_col3 = st.columns(3)
            
            with preset_col1:
                if st.form_submit_button("Weight Loss", use_container_width=True):
                    new_calories = 1800
                    new_protein = 140
                    new_carbs = 180
                    new_fat = 60
            
            with preset_col2:
                if st.form_submit_button("Maintenance", use_container_width=True):
                    new_calories = 2200
                    new_protein = 120
                    new_carbs = 275
                    new_fat = 73
            
            with preset_col3:
                if st.form_submit_button("Muscle Gain", use_container_width=True):
                    new_calories = 2600
                    new_protein = 180
                    new_carbs = 325
                    new_fat = 87
            
            # Form submission
            submit_col1, submit_col2 = st.columns(2)
            
            with submit_col1:
                save_goals = st.form_submit_button("💾 Save Goals", type="primary", use_container_width=True)
            
            with submit_col2:
                cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if save_goals:
                success = db_manager.update_user_goals(
                    user['id'], new_calories, new_protein, new_carbs, new_fat
                )
                
                if success:
                    # Update session state
                    st.session_state.user['daily_calorie_goal'] = new_calories
                    st.session_state.user['daily_protein_goal'] = new_protein
                    st.session_state.user['daily_carb_goal'] = new_carbs
                    st.session_state.user['daily_fat_goal'] = new_fat
                    st.session_state.editing_goals = False
                    
                    st.success("✅ Goals updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update goals. Please try again.")
            
            if cancel_edit:
                st.session_state.editing_goals = False
                st.rerun()
    
    # Progress tracking section
    st.markdown("---")
    st.subheader("📈 Progress Tracking")
    
    # Date range selector
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_back = st.selectbox("Show data for:", [7, 14, 30], index=0)
    
    with col2:
        end_date = st.date_input("End date", value=date.today(), max_value=date.today())
    
    with col3:
        start_date = end_date - timedelta(days=days_back-1)
        st.info(f"From: {start_date}")
    
    # Get progress data
    progress_data = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_nutrition = db_manager.get_daily_nutrition(user['id'], current_date)
        if daily_nutrition is None:
            daily_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
        
        progress_data.append({
            'Date': current_date,
            'Calories': daily_nutrition['calories'],
            'Protein': daily_nutrition['protein'],
            'Carbs': daily_nutrition['carbs'],
            'Fat': daily_nutrition['fat'],
            'Calorie_Goal': user['daily_calorie_goal'],
            'Protein_Goal': user['daily_protein_goal'],
            'Carbs_Goal': user['daily_carb_goal'],
            'Fat_Goal': user['daily_fat_goal']
        })
        current_date += timedelta(days=1)
    
    progress_df = pd.DataFrame(progress_data)
    
    if len(progress_df) > 0 and progress_df[['Calories', 'Protein', 'Carbs', 'Fat']].sum().sum() > 0:
        # Calories progress chart
        st.subheader("🔥 Calorie Progress")
        
        fig_calories = go.Figure()
        fig_calories.add_trace(go.Scatter(
            x=progress_df['Date'],
            y=progress_df['Calories'],
            mode='lines+markers',
            name='Actual Calories',
            line=dict(color='#FF6B6B', width=3)
        ))
        fig_calories.add_hline(
            y=user['daily_calorie_goal'],
            line_dash="dash",
            line_color="red",
            annotation_text="Daily Goal"
        )
        
        fig_calories.update_layout(
            title="Daily Calorie Intake vs Goal",
            xaxis_title="Date",
            yaxis_title="Calories (kcal)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_calories, use_container_width=True)
        
        # Macronutrients progress
        st.subheader("📊 Macronutrient Progress")
        
        # Create subplots for macronutrients
        col1, col2 = st.columns(2)
        
        with col1:
            # Protein chart
            fig_protein = go.Figure()
            fig_protein.add_trace(go.Scatter(
                x=progress_df['Date'],
                y=progress_df['Protein'],
                mode='lines+markers',
                name='Actual Protein',
                line=dict(color='#4ECDC4', width=3)
            ))
            fig_protein.add_hline(
                y=user['daily_protein_goal'],
                line_dash="dash",
                line_color="green",
                annotation_text="Goal"
            )
            fig_protein.update_layout(
                title="Protein Intake",
                xaxis_title="Date",
                yaxis_title="Protein (g)"
            )
            st.plotly_chart(fig_protein, use_container_width=True)
        
        with col2:
            # Carbs chart
            fig_carbs = go.Figure()
            fig_carbs.add_trace(go.Scatter(
                x=progress_df['Date'],
                y=progress_df['Carbs'],
                mode='lines+markers',
                name='Actual Carbs',
                line=dict(color='#45B7D1', width=3)
            ))
            fig_carbs.add_hline(
                y=user['daily_carb_goal'],
                line_dash="dash",
                line_color="blue",
                annotation_text="Goal"
            )
            fig_carbs.update_layout(
                title="Carbohydrate Intake",
                xaxis_title="Date",
                yaxis_title="Carbs (g)"
            )
            st.plotly_chart(fig_carbs, use_container_width=True)
        
        # Goal achievement summary
        st.subheader("🏆 Goal Achievement Summary")
        
        # Calculate achievement percentages
        avg_calories = progress_df['Calories'].mean()
        avg_protein = progress_df['Protein'].mean()
        avg_carbs = progress_df['Carbs'].mean()
        avg_fat = progress_df['Fat'].mean()
        
        cal_achievement = (avg_calories / user['daily_calorie_goal']) * 100 if user['daily_calorie_goal'] > 0 else 0
        protein_achievement = (avg_protein / user['daily_protein_goal']) * 100 if user['daily_protein_goal'] > 0 else 0
        carbs_achievement = (avg_carbs / user['daily_carb_goal']) * 100 if user['daily_carb_goal'] > 0 else 0
        fat_achievement = (avg_fat / user['daily_fat_goal']) * 100 if user['daily_fat_goal'] > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Calories Achievement",
                f"{cal_achievement:.1f}%",
                f"{avg_calories:.0f} kcal avg"
            )
        
        with col2:
            st.metric(
                "Protein Achievement",
                f"{protein_achievement:.1f}%",
                f"{avg_protein:.1f}g avg"
            )
        
        with col3:
            st.metric(
                "Carbs Achievement",
                f"{carbs_achievement:.1f}%",
                f"{avg_carbs:.1f}g avg"
            )
        
        with col4:
            st.metric(
                "Fat Achievement",
                f"{fat_achievement:.1f}%",
                f"{avg_fat:.1f}g avg"
            )
        
        # Achievement insights
        insights = []
        if cal_achievement < 80:
            insights.append("🔥 Consider increasing your calorie intake to meet your goals")
        elif cal_achievement > 120:
            insights.append("⚠️ You're exceeding your calorie goals - consider portion control")
        
        if protein_achievement < 80:
            insights.append("💪 Try to include more protein-rich foods in your diet")
        
        if len(insights) > 0:
            st.markdown("#### 💡 Insights & Recommendations")
            for insight in insights:
                st.info(insight)
    
    else:
        st.info("No nutrition data available for the selected period. Start logging meals to see your progress!")
    
    # Tips section
    with st.expander("💡 Goal Setting Tips"):
        st.markdown("""
        ### Setting Realistic Nutrition Goals
        
        **Calorie Goals:**
        - **Weight Loss:** Create a deficit of 300-500 calories below maintenance
        - **Maintenance:** Match your daily energy expenditure
        - **Weight Gain:** Add 300-500 calories above maintenance
        
        **Protein Goals:**
        - **General:** 0.8g per kg of body weight
        - **Active individuals:** 1.2-1.6g per kg
        - **Athletes:** 1.6-2.2g per kg
        
        **Carbohydrate Goals:**
        - **General:** 45-65% of total calories
        - **Low-carb:** 20-30% of total calories
        - **High-carb/athletes:** 65-70% of total calories
        
        **Fat Goals:**
        - **General:** 20-35% of total calories
        - **Minimum:** 0.5g per kg of body weight
        - **Hormone health:** At least 25% of calories
        
        **Remember:** Consult with a healthcare provider or registered dietitian for personalized recommendations.
        """)