import streamlit as st

st.markdown("""
# 🍽️ AI Calories Calculator - Dashboard Version

The AI Calories Calculator has been upgraded to a full dashboard experience!

## ✨ New Features:
- 🔐 **User Authentication** - Secure sign up/sign in
- 📊 **Interactive Dashboard** - Track your nutrition progress with charts
- 🎯 **Daily Goals** - Set and track your nutrition targets  
- 📱 **Mobile Responsive** - Optimized for all devices
- 🤖 **Enhanced AI Analysis** - Using Gemini 2.5 Flash for better accuracy
- 💾 **Data Persistence** - Your meals are saved and tracked over time

## 🚀 Getting Started:
Run the new dashboard app with:
```bash
streamlit run app.py
```

## 📋 Requirements:
- MySQL database (configure in .env file)
- Gemini API key (provided during sign-up)

---
*Original single-page calculator preserved below for reference*
""")

st.info("The dashboard version is now available in `app.py`. Run it to experience the full tracking features!")

st.markdown("---")
st.subheader("Original Calculator (Legacy)")
        st.warning("Could not initialize browser storage. API key will not be saved.")
        localS = None

    provider = st.selectbox(
        "Choose AI Provider",
        options=["Gemini", "OpenAI", "Mistral", "Llama", "Claude"],
        key="provider"
    )

    # Use a unique key for the text input to avoid conflicts with Streamlit's state
    text_input_key = f"api_key_input_{provider.lower()}"

    # Try to get the API key from local storage
    api_key_from_storage = ""
    if localS:
        stored_value = localS.getItem(f"api-{provider.lower()}")
        if stored_value:
            api_key_from_storage = stored_value

    # Get API key from user, using the stored value as the default
    api_key = st.text_input(
        f"{provider} API Key",
        type="password",
        key=text_input_key,
        value=api_key_from_storage
    )

    # Save the new key to local storage if it has changed
    if localS and api_key != api_key_from_storage:
        localS.setItem(f"api-{provider.lower()}", api_key)

    if provider == "Gemini":
        model_choice = st.selectbox(
            "Gemini Model",
            options=[
                ("gemini-2.5-pro", "gemini-2.5-pro"),
                ("gemini-2.5-flash", "gemini-2.5-flash"),
                ("gemini-1.5-pro-latest", "gemini-1.5-pro-latest"),
                ("gemini-1.5-pro", "gemini-1.5-pro"),
                ("gemini-1.0-pro", "gemini-1.0-pro")
            ],
            format_func=lambda x: x[1],
            key="model-gemini"
        )
    elif provider == "OpenAI":
        model_choice = st.selectbox(
            "OpenAI Model",
            options=[
                ("gpt-5", "gpt-5"),
                ("gpt-4.1", "gpt-4.1"),
                ("gpt-4o", "gpt-4o"),
                ("gpt-4", "gpt-4"),
                ("gpt-4-mini", "gpt-4-mini"),
                ("gpt-3.5-turbo", "gpt-3.5-turbo")
            ],
            format_func=lambda x: x[1],
            key="model-openai"
        )
    elif provider == "Mistral":
        model_choice = st.selectbox(
            "Mistral Model",
            options=[
                ("mistral-large-latest", "mistral-large-latest"),
                ("mistral-medium", "mistral-medium"),
                ("mistral-small", "mistral-small")
            ],
            format_func=lambda x: x[1],
            key="model-mistral"
        )
    elif provider == "Llama":
        model_choice = st.selectbox(
            "Llama Model",
            options=[
                ("llama-3.1-405b-instruct", "Llama 3.1 405B"),
                ("llama-3.1-70b-versatile", "Llama 3.1 70B"),
                ("llama-3.1-8b-instant", "Llama 3.1 8B"),
                ("llama-scout-agentic", "Llama Scout (Agentic)"),
                ("llama-3-70b", "Llama 3 70B"),
                ("llama-3-8b", "Llama 3 8B"),
            ],
            format_func=lambda x: x[1],
            key="model-llama"
        )
    elif provider == "Claude":
        model_choice = st.selectbox(
            "Claude Model",
            options=[
                ("claude-3-opus-20240229", "Claude 3 Opus"),
                ("claude-3-sonnet-20240229", "Claude 3 Sonnet"),
                ("claude-3-haiku-20240307", "Claude 3 Haiku"),
            ],
            format_func=lambda x: x[1],
            key="model-claude"
        )
    st.markdown("""<hr style='margin:10px 0 10px 0;border:1px solid #eee;'>""", unsafe_allow_html=True)

    with st.expander("Learn More About Privacy"):
        st.info(
            """
            **Your Privacy is Important**

            *   **API Key Storage**: Your API key is saved *only* in your browser's local storage. It is never sent to or stored on our servers.
            *   **Chat & Image Data**: Your prompts, conversations, and uploaded images are processed for the analysis and are not stored.
            *   **Open Source**: This project is open source under the Apache 2.0 License. Any modifications should credit the original creator, JThweb.
            """,
            icon="🔒"
        )

if not api_key:
    st.warning(f"Please enter your {provider} API key in the sidebar.")
    st.stop()
else:
    if provider == "Gemini":
        genai.configure(api_key=api_key)
    # For OpenAI, configuration will be handled in the OpenAI logic

# --- Function Definitions ---

def get_gemini_response(input_prompt, image_parts, user_prompt, model_id):
    """
    Calls the Gemini API to get a response based on an image and text prompts.
    
    Args:
        input_prompt (str): The main system prompt for the model.
        image_parts (list): A list containing the image data and mime type.
        user_prompt (str): Additional text input from the user.
        model_id (str): The ID of the model to use for the request.

    Returns:
        str: The text response from the Gemini model.
    """
    try:
        model = genai.GenerativeModel(model_id)
        response = model.generate_content([input_prompt, image_parts[0], user_prompt])
        return response.text
    except Exception as e:
        st.error(f"An error occurred with the JThweb API: {e}")
        return None

def setup_image_data(uploaded_file_or_camera_input):
    """
    Processes an uploaded file or camera input into the format needed for the Gemini API.
    
    Args:
        uploaded_file_or_camera_input: The file object from st.file_uploader or st.camera_input.
        
    Returns:
        list: A list containing a dictionary with the image's mime type and byte data.
    """
    if uploaded_file_or_camera_input is not None:
        # Read the file into bytes
        bytes_data = uploaded_file_or_camera_input.getvalue()
        
        # Determine the mime type
        mime_type = uploaded_file_or_camera_input.type if hasattr(uploaded_file_or_camera_input, 'type') else 'image/jpeg'

        image_parts = [
            {
                "mime_type": mime_type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        # This case should ideally not be hit if the function is called correctly
        return None

def get_openai_response(input_prompt, image_parts, user_prompt, model_id, api_key):
    """
    Calls the OpenAI API to get a response based on an image and text prompts.
    Args:
        input_prompt (str): The main system prompt for the model.
        image_parts (list): A list containing the image data and mime type (for vision models).
        user_prompt (str): Additional text input from the user.
        model_id (str): The OpenAI model name.
        api_key (str): The OpenAI API key.
    Returns:
        str: The text response from the OpenAI model.
    """
    try:
        openai.api_key = api_key
        # If image is provided and model supports vision (e.g., gpt-4o, gpt-4-vision-preview)
        if image_parts and model_id in ["gpt-4o", "gpt-4-vision-preview"]:
            image_data = image_parts[0]["data"]
            mime_type = image_parts[0]["mime_type"]
            import base64
            b64_image = base64.b64encode(image_data).decode()
            content = [
                {"type": "text", "text": input_prompt + "\n" + user_prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_image}"}}
            ]
            response = openai.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": content}],
                max_tokens=2048
            )
            return response.choices[0].message.content
        else:
            # Text-only models
            prompt = input_prompt + "\n" + user_prompt
            response = openai.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048
            )
            return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred with the OpenAI API: {e}")
        return None

# Placeholder for other AI providers

def get_other_ai_response(input_prompt, image_parts, user_prompt, model_id, api_key, provider):
    st.error(f"Provider '{provider}' is not yet supported.")
    return None

# --- Streamlit App UI ---

st.markdown("""
    <style>
    .main {background: #f8fafc;}
    .stButton>button {background: linear-gradient(90deg,#4f8cff,#38b6ff); color: white; font-weight: bold; border-radius: 8px; transition: 0.2s; box-shadow: 0 2px 8px #38b6ff44;}
    .stButton>button:hover {transform: scale(1.04); box-shadow: 0 4px 16px #38b6ff88;}
    .stTextInput>div>input {border-radius: 8px;}
    .stSelectbox>div>div {border-radius: 8px;}
    .stImage>img {border-radius: 12px; box-shadow: 0 2px 8px #0001;}
    body {background: linear-gradient(120deg, #e0e7ff 0%, #f8fafc 100%); animation: bgmove 10s infinite alternate;}
    @keyframes bgmove {0%{background-position:0 0;}100%{background-position:100vw 100vh;}}
    </style>
    <div style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;pointer-events:none;">
      <svg width="100%" height="100%">
        <circle cx="20%" cy="30%" r="120" fill="#38b6ff22">
          <animate attributeName="cy" values="30%;70%;30%" dur="8s" repeatCount="indefinite"/>
        </circle>
        <circle cx="80%" cy="60%" r="90" fill="#4f8cff22">
          <animate attributeName="cy" values="60%;20%;60%" dur="10s" repeatCount="indefinite"/>
        </circle>
      </svg>
    </div>
""", unsafe_allow_html=True)

st.header(":shallow_pan_of_food: Intelligent Food Calories Calculator", divider="rainbow")
st.markdown("""
Upload a photo or take a picture of your meal, and I'll analyze the calories and nutritional content for you!
""")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Upload an Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

with col2:
    st.subheader("Or Take a Photo")
    camera_input = st.camera_input("Take a picture (use back camera for best results)", label_visibility="collapsed")

image_input = camera_input if camera_input is not None else uploaded_file

# Initialize session state for the input field
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""

def clear_input():
    st.session_state.user_prompt = ""

user_prompt = st.text_input(
    "Optional Prompt (e.g., 'I am on a keto diet'):",
    key="user_prompt"
)

if image_input:
    image = Image.open(image_input)
    st.image(image, caption="Your Food Image", use_column_width=True)

submit = st.button("Tell Me The Total Calories", type="primary", use_container_width=True)

# --- Improved System Prompt for AI ---
input_prompt = """
You are a world-class nutritionist and food scientist. Analyze the provided food image and any user dietary notes. Identify all visible food items, estimate their portion sizes, and calculate the total calories and macronutrients (fat, carbs, protein, sugar, fiber) for each item. Use the latest scientific data and be as accurate as possible.

Go straight to the table. Do NOT include any introduction or phrases like 'Of course! As a nutritionist...'.

Present the results in a clean, readable markdown table with columns: Item, Calories (kcal), Fat (g), Fat (%DV), Carbs (g), Protein (g), Sugar (g), Fiber (g).

After the table, add a very brief summary (1-2 lines max) with key health points or suggestions if needed.

End with: _AI Calories Calculator – AI can make mistakes. Please verify information before making conclusions._
"""

# --- Main Logic ---

if submit:
    if image_input is not None:
        with st.spinner("Analyzing your meal..."):
            image_data = setup_image_data(image_input)
            if image_data:
                if provider == "Gemini":
                    response = get_gemini_response(input_prompt, image_data, user_prompt, model_choice[0])
                elif provider == "OpenAI":
                    response = get_openai_response(input_prompt, image_data, user_prompt, model_choice[0], api_key)
                else:
                    response = get_other_ai_response(input_prompt, image_data, user_prompt, model_choice[0], api_key, provider)

                if response:
                    st.subheader("Nutritional Analysis")
                    st.markdown(response)
                    # Clear the input field after a successful response
                    st.session_state.user_prompt = ""
    else:
        st.warning("Please upload an image or take a photo first!")