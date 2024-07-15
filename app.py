import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import bcrypt
import sqlite3
import requests
from io import BytesIO

# Set page configuration
st.set_page_config(page_title="Food Recognition for Dietary Tracking", layout="wide")

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

def get_gemini_response(input, image, prompt):
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT,
            password TEXT,
            profile_picture TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            scan_result TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

def update_db_schema():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in c.fetchall()]
    if 'profile_picture' not in columns:
        c.execute('ALTER TABLE users ADD COLUMN profile_picture TEXT')
    conn.commit()
    conn.close()

def add_user(username, name, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, name, password, profile_picture) VALUES (?, ?, ?, ?)', (username, name, hashed_password, None))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT username, name, password, profile_picture FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def update_profile_picture(username, profile_picture_path):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE users SET profile_picture = ? WHERE username = ?', (profile_picture_path, username))
    conn.commit()
    conn.close()

def verify_password(username, password):
    user = get_user(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        return True
    return False

def add_scan_history(username, scan_result):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO scan_history (username, scan_result) VALUES (?, ?)', (username, scan_result))
    conn.commit()
    conn.close()

def get_scan_history(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT scan_result FROM scan_history WHERE username = ?', (username,))
    history = c.fetchall()
    conn.close()
    return history

def add_feedback(username, feedback):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (username, feedback) VALUES (?, ?)', (username, feedback))
    conn.commit()
    conn.close()

# Initialize the SQLite database
init_db()
update_db_schema()

# Initialize session state variables if they don't exist
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Function to load images from URL
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# Home page with advanced layout
def home_page():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(to bottom right, #eef2f3, #8e9eab);
            font-family: 'Arial', sans-serif;
        }
        .main-container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            margin: 20px auto;
            max-width: 900px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .header-container {
            text-align: center;
            margin-bottom: 30px;
        }
        .header-text {
            font-size: 2.5em;
            color: #004080;
            margin-bottom: 10px;
        }
        .description-text {
            font-size: 1.2em;
            color: #004080;
            margin-bottom: 30px;
        }
        .nav-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }
        .nav-button {
            background-color: #004080;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: background-color 0.3s ease;
        }
        .nav-button:hover {
            background-color: #00264d;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        st.markdown("<div class='header-container'>", unsafe_allow_html=True)
        st.markdown("<div class='header-text'>Welcome to Food Recognition for Dietary Tracking</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='description-text'>Our Dietary Tracking System leverages advanced AI technology to accurately identify and label various foods displayed in images. It provides detailed information about the detected foods, including their names, positions within the image, and other relevant dietary information. This tool is designed to help users understand the contents of their meals better.</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='nav-buttons'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_button"):
                st.session_state.page = "Login"
                st.experimental_rerun()
        with col2:
            if st.button("Register", key="register_button"):
                st.session_state.page = "Register"
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.image(load_image("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgy52YPHqzGhOKGQTNY6zN8FPyt857X73sBZv5N1LzWR97dkSPIdvrNvrlw5yPPWasoM2ZCKbviQsx_xhXro0ZOWYndFFGKFSgRrp9rqUh5_KKCsXZ9FztGCdzj8kT-LOQz2X6-OiecHZZa64IrffbagDRo9RhoFWyjkmJmBR2PIB33qsMbUuBhxAxvr-rq/s2240/food_scan_image.jpg"), caption="Dietary Tracking System")
        st.image(load_image("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgIo6GFeyJepS6WUxR0uVGbScbCy7hWSjz_DczgokyNu0D-f7dKK3ecNfOCmMg88RJ-U0VALQ_KxDQl6iIVsiAmvGXNcmjX_s3eoZSSYMe4GUO_XoX-XF6pJ8NMqbuM30Ovq8Von6NQGSkdnv_B5DxGxBy1ySM7g_M6nMVvtXe9izzHB5LXr7OdkUKXbZ2x/s1366/homepage.png"), caption="")

        st.markdown("</div>", unsafe_allow_html=True)

# Login page
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_password(username, password):
            user = get_user(username)
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state.page = "Main App"
            st.success(f"Welcome {user[1]}!")
            st.experimental_rerun()
        else:
            st.error("Username/password is incorrect")
    if st.button("Back"):
        st.session_state.page = "Home"
        st.experimental_rerun()

# Registration page
def registration_page():
    st.title("Register")
    username = st.text_input("Username")
    name = st.text_input("Name")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if get_user(username):
            st.error("Username already exists! Please choose a different username.")
        else:
            add_user(username, name, password)
            st.success("Registration successful! You can now login.")
    if st.button("Back"):
        st.session_state.page = "Home"
        st.experimental_rerun()

# Scan History page
def scan_history_page():
    st.title("Your Scan History")
    history = get_scan_history(st.session_state["username"])
    if history:
        for record in history:
            st.write(f"Scan Result: {record[0]}")
    else:
        st.write("No scan history found.")

# Feedback page
def feedback_page():
    st.title("Feedback")
    if "username" in st.session_state:
        username = st.session_state["username"]
    else:
        st.error("Please login to provide feedback")
        return

    feedback = st.text_area("Provide your feedback")
    if st.button("Submit Feedback"):
        add_feedback(username, feedback)
        st.success("Feedback submitted successfully")

# Profile page
def profile_page():
    st.title("Profile")
    user = get_user(st.session_state["username"])
    if user:
        profile_picture_path = user[3] if user[3] else "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjiJ2fA_6qbVyMQYmadZvugF7fOmZqdVJdDP9-KznNQoaD9NaRuxzeHh5h_xThENPV1dq-SpQny5Gvts5HkD_ajrhz5ZvHtKhyphenhyphenjPMTHgt7xOn_HzPzLYjIXRknb7wQvnBW5Bigy_Y1h2AECvodR-21upP2jOUYDO8Cbp3SSK9xDKU1te4yOyw1ZpW0kU0B_/s200/default_profile_picture.jpg"
        st.image(load_image(profile_picture_path), caption="Profile Picture", width=150)

        uploaded_file = st.file_uploader("Upload a new profile picture", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            profile_picture_path = os.path.join("C:/Users/yusuo/Downloads/", uploaded_file.name)
            with open(profile_picture_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            update_profile_picture(st.session_state["username"], profile_picture_path)
            st.success("Profile picture updated successfully!")
            st.experimental_rerun()

        st.write(f"Username: {user[0]}")
        st.write(f"Name: {user[1]}")
    else:
        st.error("User not found")

    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state.page = "Home"
        st.experimental_rerun()

# Main app function
def main_app():
    st.header('Dietary Tracking with Google Gemini')
    input_prompt = st.text_input("Input prompt: ", key='input')
    uploaded_file = st.file_uploader("Choose an image of the food or meal", type=["jpg", 'jpeg', 'png'])
    image = ""
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    submit = st.button("Scan the Food")

    input_prompt_text = """
    You have to identify different types of food in images. 
    The system should accurately detect and label various foods displayed in the image, providing the name 
    of the food and its location within the image (e.g., bottom left, right corner, etc.). The output should include a comprehensive report or display showing the
    identified foods, their positions, names, and corresponding dietary details.
    """

    if submit and uploaded_file is not None:
        image_data = input_image_details(uploaded_file)
        response = get_gemini_response(input_prompt_text, image_data, input_prompt)
        st.subheader("Food Scan Report: ")
        st.write(response)
        add_scan_history(st.session_state["username"], response)

# Navigation
if st.session_state["authenticated"]:
    page = st.sidebar.radio("Go to", ["Main App", "Scan History", "Feedback", "Profile", "Logout"])

    if page == "Main App":
        main_app()
    elif page == "Scan History":
        scan_history_page()
    elif page == "Feedback":
        feedback_page()
    elif page == "Profile":
        profile_page()
    elif page == "Logout":
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state.page = "Home"
        st.experimental_rerun()
else:
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Login":
        login_page()
    elif st.session_state.page == "Register":
        registration_page()
