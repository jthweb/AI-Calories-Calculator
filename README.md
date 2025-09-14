# 🍽️ AI Calories Tracker Dashboard

A comprehensive nutrition tracking dashboard powered by AI image analysis using Google's Gemini 2.5 Flash model.

## 🌟 Features

- **🤖 AI-Powered Food Analysis** - Upload food images and get detailed nutritional breakdowns
- **📊 Interactive Dashboard** - Track daily nutrition with beautiful charts and progress indicators
- **🎯 Goal Tracking** - Set and monitor daily calorie and macronutrient goals
- **📱 Mobile Responsive** - Optimized for all devices with bottom navigation
- **🔐 User Authentication** - Secure sign up/sign in with MySQL database
- **📈 Progress Analytics** - Weekly trends and goal achievement tracking
- **🥧 Visual Insights** - Pie charts for macronutrient breakdown and progress bars

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL database
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jthweb/AI-Calories-Calculator.git
   cd AI-Calories-Calculator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Copy `.env` and update with your database credentials:
   ```bash
   DB_HOST=your_mysql_host
   DB_PORT=3306
   DB_NAME=calories_tracker
   DB_USER=your_username
   DB_PASSWORD=your_password
   SECRET_KEY=your_secret_key
   ```

4. **Set up database**
   The app will automatically create the required tables on first run.

5. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

6. **Access the app**
   Open http://localhost:8501 in your browser

## 📱 Mobile Experience

The dashboard is fully responsive with:
- Bottom navigation bar for easy mobile access
- Touch-friendly interface
- Optimized layouts for small screens
- Progressive Web App capabilities

## 🛠️ Tech Stack

- **Frontend**: Streamlit with custom CSS/HTML
- **AI Model**: Google Gemini 2.5 Flash
- **Database**: MySQL
- **Charts**: Plotly
- **Image Processing**: PIL/Pillow
- **Authentication**: Custom secure implementation

## 📊 Dashboard Pages

### 🏠 Home
- Daily nutrition overview
- Progress metrics with visual indicators
- Macronutrient pie charts
- Weekly calorie trends
- Today's meal summary

### 🤖 AI Calculator
- Food image upload/camera capture
- AI-powered nutritional analysis
- Meal type categorization
- Automatic data saving

### 🎯 Goals
- Set daily nutrition targets
- Progress tracking with charts
- Goal achievement analytics
- Preset configurations (weight loss, maintenance, muscle gain)

### ⚙️ Settings
- Profile management
- API key configuration
- Data export options
- Account preferences

## 🔧 Database Schema

The app creates three main tables:
- `users` - User accounts and preferences
- `meals` - Meal records with nutrition data
- `meal_items` - Individual food items per meal

## 🛡️ Security & Privacy

- Passwords are securely hashed
- API keys are encrypted in database
- Images are processed in real-time (not stored)
- Local browser storage for session management

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powerful food analysis
- Streamlit for the fantastic web framework
- Plotly for beautiful interactive charts
- Original concept by JThweb

## 📞 Support

For issues and feature requests, please open an issue on GitHub.

---

**Live Demo**: https://ai-calories-calculator.streamlit.app/