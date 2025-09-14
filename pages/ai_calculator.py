import streamlit as st
import google.generativeai as genai
from PIL import Image
from database import db_manager
import re
import json

def show_ai_calculator():
    """Show the AI Calories Calculator page"""
    user = st.session_state.user
    
    # Configure Gemini with user's API key
    if user['gemini_api_key']:
        genai.configure(api_key=user['gemini_api_key'])
    else:
        st.error("No Gemini API key found. Please update your API key in Settings.")
        return
    
    st.title("🤖 AI Calories Calculator")
    st.markdown("Upload a photo of your meal and let AI analyze the nutritional content!")
    
    # Image input
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.subheader("📤 Upload an Image")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    with col2:
        st.subheader("📸 Or Take a Photo")
        camera_input = st.camera_input("Take a picture", label_visibility="collapsed")
    
    image_input = camera_input if camera_input is not None else uploaded_file
    
    # Additional inputs
    col1, col2 = st.columns(2)
    
    with col1:
        meal_type = st.selectbox(
            "Meal Type",
            options=["breakfast", "lunch", "dinner", "snack"],
            help="Select the type of meal for better tracking"
        )
    
    with col2:
        user_prompt = st.text_input(
            "Additional Notes (Optional)",
            placeholder="e.g., 'I'm on a keto diet', 'Large portion', etc.",
            help="Provide context to improve AI analysis accuracy"
        )
    
    # Display image if uploaded
    if image_input:
        image = Image.open(image_input)
        st.image(image, caption="Your Food Image", use_column_width=True)
    
    # Analyze button
    analyze_button = st.button("🔬 Analyze with Gemini AI", type="primary", use_container_width=True)
    
    if analyze_button:
        if image_input is None:
            st.warning("Please upload an image or take a photo first!")
            return
        
        with st.spinner("🤖 AI is analyzing your meal..."):
            # Setup image data
            image_data = setup_image_data(image_input)
            if image_data:
                # Get AI response
                response = get_gemini_response(image_data, user_prompt)
                
                if response:
                    st.success("✅ Analysis complete!")
                    
                    # Display AI analysis
                    st.subheader("📊 Nutritional Analysis")
                    st.markdown(response)
                    
                    # Parse nutrition data from response
                    nutrition_data = parse_nutrition_from_response(response)
                    
                    # Save to database
                    success = db_manager.save_meal_analysis(
                        user_id=user['id'],
                        meal_type=meal_type,
                        ai_analysis=response,
                        nutrition_data=nutrition_data,
                        image_name=f"meal_{user['id']}_{meal_type}.jpg"
                    )
                    
                    if success:
                        st.success("💾 Meal data saved to your profile!")
                        
                        # Option to add another meal
                        if st.button("Add Another Meal"):
                            st.rerun()
                    else:
                        st.error("Failed to save meal data. Please try again.")
                else:
                    st.error("Failed to analyze image. Please try again.")

def setup_image_data(uploaded_file_or_camera_input):
    """Process image for Gemini API"""
    if uploaded_file_or_camera_input is not None:
        bytes_data = uploaded_file_or_camera_input.getvalue()
        mime_type = uploaded_file_or_camera_input.type if hasattr(uploaded_file_or_camera_input, 'type') else 'image/jpeg'
        
        return [{
            "mime_type": mime_type,
            "data": bytes_data
        }]
    return None

def get_gemini_response(image_parts, user_prompt):
    """Get response from Gemini 2.5 Flash model"""
    try:
        # Enhanced prompt for better nutrition analysis
        system_prompt = """
        You are an expert nutritionist and food scientist. Analyze the provided food image and identify all visible food items with their estimated portion sizes. Calculate the total calories and macronutrients for each item using the latest scientific nutritional data.

        IMPORTANT: Respond with a structured analysis that includes:
        1. A detailed markdown table with columns: Item, Portion Size, Calories (kcal), Protein (g), Carbs (g), Fat (g), Fiber (g), Sugar (g)
        2. Total nutritional summary at the end
        3. Brief health insights (1-2 sentences)

        Be as accurate as possible with portion size estimation and use standard nutritional values. Consider cooking methods and food preparation when calculating nutritional content.

        Format your response clearly with proper markdown formatting.
        
        End with: _AI Calories Calculator – AI can make mistakes. Please verify information before making conclusions._
        """
        
        full_prompt = system_prompt
        if user_prompt:
            full_prompt += f"\n\nAdditional context from user: {user_prompt}"
        
        # Use Gemini 2.5 Flash model
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([full_prompt, image_parts[0]])
        
        return response.text
        
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return None

def parse_nutrition_from_response(response):
    """Parse nutrition data from AI response"""
    nutrition_data = {
        'total_calories': 0,
        'total_protein': 0,
        'total_carbs': 0,
        'total_fat': 0,
        'total_sugar': 0,
        'total_fiber': 0,
        'items': []
    }
    
    try:
        # Look for total values in the response
        lines = response.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Extract total calories
            if 'total' in line_lower and 'calorie' in line_lower:
                calories_match = re.search(r'(\d+(?:\.\d+)?)', line)
                if calories_match:
                    nutrition_data['total_calories'] = float(calories_match.group(1))
            
            # Extract protein
            if 'protein' in line_lower and 'total' in line_lower:
                protein_match = re.search(r'(\d+(?:\.\d+)?)', line)
                if protein_match:
                    nutrition_data['total_protein'] = float(protein_match.group(1))
            
            # Extract carbs
            if ('carb' in line_lower or 'carbohydrate' in line_lower) and 'total' in line_lower:
                carbs_match = re.search(r'(\d+(?:\.\d+)?)', line)
                if carbs_match:
                    nutrition_data['total_carbs'] = float(carbs_match.group(1))
            
            # Extract fat
            if 'fat' in line_lower and 'total' in line_lower:
                fat_match = re.search(r'(\d+(?:\.\d+)?)', line)
                if fat_match:
                    nutrition_data['total_fat'] = float(fat_match.group(1))
        
        # If we couldn't parse totals, try to extract from table format
        if nutrition_data['total_calories'] == 0:
            # Look for table rows and sum up values
            table_pattern = r'\|[^|]*\|[^|]*\|[^|]*(\d+(?:\.\d+)?)[^|]*\|[^|]*(\d+(?:\.\d+)?)[^|]*\|[^|]*(\d+(?:\.\d+)?)[^|]*\|[^|]*(\d+(?:\.\d+)?)[^|]*\|'
            matches = re.findall(table_pattern, response)
            
            for match in matches:
                try:
                    calories = float(match[0]) if match[0] else 0
                    protein = float(match[1]) if match[1] else 0
                    carbs = float(match[2]) if match[2] else 0
                    fat = float(match[3]) if match[3] else 0
                    
                    nutrition_data['total_calories'] += calories
                    nutrition_data['total_protein'] += protein
                    nutrition_data['total_carbs'] += carbs
                    nutrition_data['total_fat'] += fat
                except:
                    continue
    
    except Exception as e:
        st.warning(f"Could not parse nutrition data: {e}")
    
    return nutrition_data