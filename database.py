import mysql.connector
from mysql.connector import Error
import streamlit as st
import hashlib
import os
from dotenv import load_dotenv
from datetime import datetime, date
import json

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '3306')
        self.database = os.getenv('DB_NAME', 'calories_tracker')
        self.user = os.getenv('DB_USER', 'placeholder_username')
        self.password = os.getenv('DB_PASSWORD', 'placeholder_password')
        
    def get_connection(self):
        """Create and return a database connection"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Error as e:
            st.error(f"Database connection error: {e}")
            return None
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            connection = self.get_connection()
            if connection is None:
                return False
                
            cursor = connection.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    gemini_api_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    daily_calorie_goal INT DEFAULT 2000,
                    daily_protein_goal INT DEFAULT 150,
                    daily_carb_goal INT DEFAULT 250,
                    daily_fat_goal INT DEFAULT 65
                )
            """)
            
            # Create meals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    meal_date DATE NOT NULL,
                    meal_time TIME NOT NULL,
                    meal_type ENUM('breakfast', 'lunch', 'dinner', 'snack') NOT NULL,
                    image_name VARCHAR(255),
                    total_calories DECIMAL(10,2) DEFAULT 0,
                    total_protein DECIMAL(10,2) DEFAULT 0,
                    total_carbs DECIMAL(10,2) DEFAULT 0,
                    total_fat DECIMAL(10,2) DEFAULT 0,
                    total_sugar DECIMAL(10,2) DEFAULT 0,
                    total_fiber DECIMAL(10,2) DEFAULT 0,
                    ai_analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create meal_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meal_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    meal_id INT NOT NULL,
                    item_name VARCHAR(255) NOT NULL,
                    calories DECIMAL(10,2) DEFAULT 0,
                    protein DECIMAL(10,2) DEFAULT 0,
                    carbs DECIMAL(10,2) DEFAULT 0,
                    fat DECIMAL(10,2) DEFAULT 0,
                    sugar DECIMAL(10,2) DEFAULT 0,
                    fiber DECIMAL(10,2) DEFAULT 0,
                    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE
                )
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            st.error(f"Database initialization error: {e}")
            return False
    
    def hash_password(self, password):
        """Hash a password for storing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password, gemini_api_key):
        """Create a new user"""
        try:
            connection = self.get_connection()
            if connection is None:
                return False, "Database connection failed"
                
            cursor = connection.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, gemini_api_key)
                VALUES (%s, %s, %s, %s)
            """, (username, email, password_hash, gemini_api_key))
            
            connection.commit()
            cursor.close()
            connection.close()
            return True, "User created successfully"
            
        except Error as e:
            if "Duplicate entry" in str(e):
                return False, "Username or email already exists"
            return False, f"Database error: {e}"
    
    def authenticate_user(self, username, password):
        """Authenticate a user and return user data"""
        try:
            connection = self.get_connection()
            if connection is None:
                return False, None, "Database connection failed"
                
            cursor = connection.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                SELECT id, username, email, gemini_api_key, daily_calorie_goal,
                       daily_protein_goal, daily_carb_goal, daily_fat_goal
                FROM users 
                WHERE username = %s AND password_hash = %s
            """, (username, password_hash))
            
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user:
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'gemini_api_key': user[3],
                    'daily_calorie_goal': user[4],
                    'daily_protein_goal': user[5],
                    'daily_carb_goal': user[6],
                    'daily_fat_goal': user[7]
                }
                return True, user_data, "Login successful"
            else:
                return False, None, "Invalid username or password"
                
        except Error as e:
            return False, None, f"Database error: {e}"
    
    def save_meal_analysis(self, user_id, meal_type, ai_analysis, nutrition_data, image_name=None):
        """Save meal analysis to database"""
        try:
            connection = self.get_connection()
            if connection is None:
                return False
                
            cursor = connection.cursor()
            
            # Insert meal record
            cursor.execute("""
                INSERT INTO meals (user_id, meal_date, meal_time, meal_type, image_name,
                                 total_calories, total_protein, total_carbs, total_fat,
                                 total_sugar, total_fiber, ai_analysis)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                date.today(),
                datetime.now().time(),
                meal_type,
                image_name,
                nutrition_data.get('total_calories', 0),
                nutrition_data.get('total_protein', 0),
                nutrition_data.get('total_carbs', 0),
                nutrition_data.get('total_fat', 0),
                nutrition_data.get('total_sugar', 0),
                nutrition_data.get('total_fiber', 0),
                ai_analysis
            ))
            
            meal_id = cursor.lastrowid
            
            # Insert individual meal items if provided
            if 'items' in nutrition_data:
                for item in nutrition_data['items']:
                    cursor.execute("""
                        INSERT INTO meal_items (meal_id, item_name, calories, protein,
                                              carbs, fat, sugar, fiber)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        meal_id,
                        item['name'],
                        item.get('calories', 0),
                        item.get('protein', 0),
                        item.get('carbs', 0),
                        item.get('fat', 0),
                        item.get('sugar', 0),
                        item.get('fiber', 0)
                    ))
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            st.error(f"Error saving meal: {e}")
            return False
    
    def get_daily_nutrition(self, user_id, target_date=None):
        """Get daily nutrition summary for a user"""
        if target_date is None:
            target_date = date.today()
            
        try:
            connection = self.get_connection()
            if connection is None:
                return None
                
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(total_calories), 0) as total_calories,
                    COALESCE(SUM(total_protein), 0) as total_protein,
                    COALESCE(SUM(total_carbs), 0) as total_carbs,
                    COALESCE(SUM(total_fat), 0) as total_fat,
                    COALESCE(SUM(total_sugar), 0) as total_sugar,
                    COALESCE(SUM(total_fiber), 0) as total_fiber
                FROM meals 
                WHERE user_id = %s AND meal_date = %s
            """, (user_id, target_date))
            
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result:
                return {
                    'calories': float(result[0]),
                    'protein': float(result[1]),
                    'carbs': float(result[2]),
                    'fat': float(result[3]),
                    'sugar': float(result[4]),
                    'fiber': float(result[5])
                }
            return None
            
        except Error as e:
            st.error(f"Error getting daily nutrition: {e}")
            return None
    
    def get_meals_by_date(self, user_id, target_date=None):
        """Get all meals for a specific date"""
        if target_date is None:
            target_date = date.today()
            
        try:
            connection = self.get_connection()
            if connection is None:
                return []
                
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT id, meal_type, meal_time, total_calories, total_protein,
                       total_carbs, total_fat, ai_analysis, image_name
                FROM meals 
                WHERE user_id = %s AND meal_date = %s
                ORDER BY meal_time
            """, (user_id, target_date))
            
            meals = cursor.fetchall()
            cursor.close()
            connection.close()
            
            meal_list = []
            for meal in meals:
                meal_list.append({
                    'id': meal[0],
                    'type': meal[1],
                    'time': meal[2],
                    'calories': float(meal[3]),
                    'protein': float(meal[4]),
                    'carbs': float(meal[5]),
                    'fat': float(meal[6]),
                    'analysis': meal[7],
                    'image_name': meal[8]
                })
            
            return meal_list
            
        except Error as e:
            st.error(f"Error getting meals: {e}")
            return []
    
    def update_user_goals(self, user_id, calorie_goal, protein_goal, carb_goal, fat_goal):
        """Update user's daily nutrition goals"""
        try:
            connection = self.get_connection()
            if connection is None:
                return False
                
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET daily_calorie_goal = %s, daily_protein_goal = %s,
                    daily_carb_goal = %s, daily_fat_goal = %s
                WHERE id = %s
            """, (calorie_goal, protein_goal, carb_goal, fat_goal, user_id))
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            st.error(f"Error updating goals: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()