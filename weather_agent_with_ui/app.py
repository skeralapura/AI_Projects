# -*- coding: utf-8 -*-
########################################################################################################################
# 01 - IMPORT LIBRARIES
########################################################################################################################
# Load env variables for .env file
from dotenv import load_dotenv
import streamlit as st

import os
import requests
import asyncio
########################################################################################################################
# 02 - LOAD ENV & AGENT MODULES
########################################################################################################################

load_dotenv()
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

########################################################################################################################
# 03 - DEFINE WEATHER TOOL
########################################################################################################################

@tool
def get_weather(query: str):
    """Get the current weather information for a specified city."""

    # Clean the input string
    try:
        #lat_lon = query.strip().split(',')
        #latitude = float(lat_lon[0].strip())
        #longitude = float(lat_lon[1].strip())
        coords = query.replace(" ", "").split(',')
        lat, lon = float(coords[0]), float(coords[1])
    except:
        lat, lon = 39.7684, -86.1581 # Indianapolis default

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
    try:
        data = requests.get(url).json()
        temperature = data["current"]["temperature_2m"]
        wind_speed = data["current"]["wind_speed_10m"]
        return f"The current temperature is 🌡️ {temperature}°C with a wind speed of 💨 {wind_speed} m/s."
    except Exception as e:
        return f"Failed to fetch weather data: {str(e)}"

########################################################################################################################
# 04 - STREAMLIT CODE FOR UI & SESSION STATE
########################################################################################################################

# Initialize history in session state if it doesn't exist
if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Model Settings")
    
    # 1. Model Selection
    selected_model = st.selectbox(
        "Choose LLM Model:",
        ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        index=0
    )
    
    # 2. Temperature Slider (0.0 to 1.0)
    selected_temp = st.slider(
        "Temperature (Randomness):",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )

    # System Message (Personality)
    system_msg = st.text_area(
        "System Message (Personality):",
        value="Ex: Answer like a pirate",
        help="This defines how the AI behaves."
    )
    
    st.divider()

# --- SIDEBAR HISTORY ---
with st.sidebar:
    st.title("📜 Lookup History")
    if not st.session_state.history:
        st.write("No lookups yet.")
    else:
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Query: {entry['query']}", expanded=False):
                st.write(f"**Result:** {entry['response']}")
    
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

########################################################################################################################
# 05 - DEFINE SYSTEM PROMPT AND INITIALIZE AGENT
########################################################################################################################

# Define the system prompt
SYSTEM_PROMPT = """You are a helpful assistant that can access the weather for any city.
Use the provided tools to answer questions about the weather. Input should be latitude and longitude of the city as two numbers separated by a comma (e.g., '40.7128, -74.0060')."""

# Initialize the language model
# --- INITIALIZE AGENT WITH DYNAMIC VALUES ---
# The LLM now uses the values chosen in the sidebar
#llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm = ChatOpenAI(
    model=selected_model, 
    temperature=selected_temp
)
agent = create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt= SYSTEM_PROMPT + " " + system_msg
)

########################################################################################################################
# 06 - MAIN INTERFACE
########################################################################################################################

st.set_page_config(page_title="AI Weather Agent", page_icon="🌤️", layout="wide")
st.title("🌤️ AI Weather Agent")
st.write("Ask about the weather in any city!")

# Input field for user query
user_input = st.text_input("Enter city or question:", placeholder="What's the weather in Indianapolis?")

# Response field logic
if st.button("Get Weather"):
    if user_input:
        with st.spinner("Agent is thinking..."):
            # Run the agent synchronously
            result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
            answer = result['messages'][-1].content
            
            # Save to history session state
            st.session_state.history.append({
                "query": user_input,
                "response": answer
            })
            
            # 1. Save to history
            st.subheader("Current Result")
            st.info(answer)
            st.success(answer)

            # 2. Save to 'last_result' so it persists after the rerun
            st.session_state.last_result = answer

            # Force a rerun to update the sidebar history immediately
            st.rerun()

    else:
        st.warning("Please enter a city name or question.")

# --- DISPLAY AREA ---
# This part runs every time the script reruns
if st.session_state.last_result:
    st.subheader("Current Result")
    st.info(st.session_state.last_result)