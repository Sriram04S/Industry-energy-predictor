import streamlit as st
import pickle
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv  

# Load API key
load_dotenv()
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate API Key
if not GENAI_API_KEY:
    st.error("❌ Gemini API Key not found. Please check your .env file or environment variables.")
    st.stop()

# Configure Google Gemini AI
genai.configure(api_key=GENAI_API_KEY)

# Load the saved Linear Regression model
try:
    with open("regression_model.pkl", "rb") as file:
        model = pickle.load(file)
except FileNotFoundError:
    st.error("❌ Model file not found! Ensure 'regression_model.pkl' is in the correct directory.")
    st.stop()

# Function to get chatbot response from Gemini API
def get_chat_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# Streamlit UI
def main():
    st.set_page_config(page_title="Energy Predictor & AI Chatbot", layout="wide")

    # Sidebar Navigation
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)  # AI Icon
    st.sidebar.title("Navigation")
    selected_tab = st.sidebar.radio("Go to:", ["📊 Energy Prediction", "🤖 AI Chatbot"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 About the App")
    st.sidebar.info("This app predicts energy consumption based on input data and provides AI-powered responses using Google Gemini.")

    if selected_tab == "📊 Energy Prediction":
        energy_prediction_ui()
    elif selected_tab == "🤖 AI Chatbot":
        chatbot_ui()

# ---- Energy Prediction UI ----
def energy_prediction_ui():
    st.markdown("<h2 style='color:#1F51FF'>📉 Energy Consumption Prediction</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        lagging_power = st.number_input("⚡ Lagging Current Reactive Power (kVarh)", min_value=0.0, step=0.1)
        leading_power = st.number_input("🔋 Leading Current Reactive Power (kVarh)", min_value=0.0, step=0.1)
        co2_emissions = st.number_input("🌍 CO2 Emissions (tCO2)", min_value=0.0, step=0.1)
        lagging_power_factor = st.slider("📊 Lagging Current Power Factor", 0.0, 1.0, 0.5)
        leading_power_factor = st.slider("💡 Leading Current Power Factor", 0.0, 1.0, 0.5)

    with col2:
        nsm = st.number_input("⏳ NSM (Time of Day)", min_value=0, step=1)
        is_weekday = st.radio("📅 Week Status", ["Weekday", "Weekend"])
        days_of_week = st.selectbox("📆 Day of Week", ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        load_type = st.selectbox("🔌 Load Type", ["Light Load", "Medium Load", "Maximum Load"])

    # Prepare input data
    user_input = pd.DataFrame({
        "Lagging_Current_Reactive.Power_kVarh": [lagging_power],
        "Leading_Current_Reactive_Power_kVarh": [leading_power],
        "CO2(tCO2)": [co2_emissions],
        "Lagging_Current_Power_Factor": [lagging_power_factor],
        "Leading_Current_Power_Factor": [leading_power_factor],
        "NSM": [nsm],
        "WeekStatus_Weekday": [1 if is_weekday == "Weekday" else 0],
        "WeekStatus_Weekend": [1 if is_weekday == "Weekend" else 0],
        "Day_of_week_Friday": [1 if days_of_week == "Friday" else 0],
        "Day_of_week_Monday": [1 if days_of_week == "Monday" else 0],
        "Day_of_week_Saturday": [1 if days_of_week == "Saturday" else 0],
        "Day_of_week_Sunday": [1 if days_of_week == "Sunday" else 0],
        "Day_of_week_Thursday": [1 if days_of_week == "Thursday" else 0],
        "Day_of_week_Tuesday": [1 if days_of_week == "Tuesday" else 0],
        "Day_of_week_Wednesday": [1 if days_of_week == "Wednesday" else 0],
        "Load_Type_Light_Load": [1 if load_type == "Light Load" else 0],
        "Load_Type_Maximum_Load": [1 if load_type == "Maximum Load" else 0],
        "Load_Type_Medium_Load": [1 if load_type == "Medium Load" else 0]
    })

    # Reorder columns to match model's training data
    column_order = [
        "Lagging_Current_Reactive.Power_kVarh", "Leading_Current_Reactive_Power_kVarh", "CO2(tCO2)",
        "Lagging_Current_Power_Factor", "Leading_Current_Power_Factor", "NSM",
        "WeekStatus_Weekday", "WeekStatus_Weekend",
        "Day_of_week_Friday", "Day_of_week_Monday", "Day_of_week_Saturday", "Day_of_week_Sunday",
        "Day_of_week_Thursday", "Day_of_week_Tuesday", "Day_of_week_Wednesday",
        "Load_Type_Light_Load", "Load_Type_Maximum_Load", "Load_Type_Medium_Load"
    ]
    user_input = user_input[column_order]

    # Predict Energy Consumption
    if st.button("⚡ Predict Energy Consumption", use_container_width=True):
        try:
            prediction = model.predict(user_input)
            st.success(f"🔋 Predicted Energy Consumption: {prediction[0]:.3f} kWh")
        except Exception as e:
            st.error(f"⚠ Prediction error: {e}")

# ---- AI Chatbot UI ----
def chatbot_ui():
    st.markdown("<h2 style='color:#FF5733'>🤖 AI Chatbot</h2>", unsafe_allow_html=True)
    st.markdown("💬 Ask me anything related to AI, energy consumption, or general knowledge!")

    user_query = st.text_area("💡 Type your question here:", height=150, placeholder="E.g., How does energy consumption impact sustainability?")

    if st.button("🎯 Get AI Response", use_container_width=True):
        if user_query.strip():
            with st.spinner("🤖 Thinking..."):
                response = get_chat_response(user_query)
            st.markdown(f"**🧠 AI:** {response}")
        else:
            st.warning("⚠ Please enter a question.")

if __name__ == "__main__":
    main()
