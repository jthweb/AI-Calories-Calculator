### Food Calories calculator APP
from dotenv import load_dotenv

load_dotenv() ## load all the environment variables

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to load Google Gemini Pro API And get response

def get_gemini_repsonse(input,image,prompt):
    model=genai.GenerativeModel('gemini-2.5-flash')
    response=model.generate_content([input,image[0],prompt])
    return response.text

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")
    
##initialize our streamlit app

st.set_page_config(page_title="Intelligent Food Calories Calculator")

st.header("Intelligent Food Calories Calculator")
input=st.text_input("Input Prompt (Optional): ",key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image=""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)


submit=st.button("Tell me the total calories")

input_prompt="""
You are a nutrition expert. Analyze the food items from the image and calculate the total calorie content. List each item with its: calories, % daily fat intake, carbs, protein, and other key macros in the following table format. Remove the intro and conclusion bit — no need for any summary. Format neatly and presentably:

| **Item**         | **Calories (kcal)** | **Fat (g)** | **Fat (%DV)** | **Carbs (g)** | **Protein (g)** | **Sugar (g)** | **Fiber (g)** |
|------------------|---------------------|-------------|---------------|---------------|-----------------|---------------|---------------|
| Item 1           | ___                 | ___         | ___           | ___           | ___             | ___           | ___           |
| ...              | ...                 | ...         | ...           | ...           | ...             | ...           | ...           |

| **Total**        | **___ kcal**        | **___ g**   | **___ %DV**    | **___ g**     | **___ g**       | **___ g**     | **___ g**     |

"""

## If submit button is clicked

if submit:
    image_data=input_image_setup(uploaded_file)
    response=get_gemini_repsonse(input_prompt,image_data,input)
    st.subheader("The Calories in this food is")
    st.write(response)


