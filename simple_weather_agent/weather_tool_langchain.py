# -*- coding: utf-8 -*-
########################################################################################################################
# 01 - IMPORT LIBRARIES
########################################################################################################################

from dotenv import load_dotenv
import streamlit as st

import os
import requests
import asyncio
########################################################################################################################
# 02 - LOAD ENV & AGENT MODULES
########################################################################################################################
print("Loading env variables")
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
    print("[debug] get_weather called")

    # Parse latitude and longitude from query
    try:
        lat_lon = query.strip().split(',')
        latitude = float(lat_lon[0].strip())
        longitude = float(lat_lon[1].strip())
        print(f"Latitude: {latitude}, Longitude: {longitude}")
    except:
        latitude, longitude = 39.7684, -86.1581 # Indianapolis default

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    response = requests.get(url)
    data = response.json()
    temperature = data["current"]["temperature_2m"]
    wind_speed = data["current"]["wind_speed_10m"]
    return f"The current temperature is {temperature}°C with a wind speed of {wind_speed} m/s."

    #return Weather(city=query, temperature=temperature, wind_speed=wind_speed)

########################################################################################################################
# 04 - DEFINE SYSTEM PROMPT AND INITIALIZE AGENT
########################################################################################################################

# Define the system prompt
SYSTEM_PROMPT = """You are a helpful assistant that can access the weather for any city.
Use the provided tools to answer questions about the weather. Input should be latitude and longitude of the city as two numbers separated by a comma (e.g., '40.7128, -74.0060')."""

# Initialize the language model
# Ensure OPENAI_API_KEY environment variable is set
llm = ChatOpenAI(model="gpt-4o", temperature=0)
agent = create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt=SYSTEM_PROMPT
)

########################################################################################################################
# 05 - STREAMLIT CODE FOR UI
########################################################################################################################

st.set_page_config(page_title="AI Weather Agent", page_icon="🌤️")
st.title("🌤️ AI Weather Agent")
st.write("Ask about the weather in any city!")

# Input field for user query
user_input = st.text_input("Enter city or question:", placeholder="What's the weather in Indianapolis?")

# Response field logic
if st.button("Get Weather"):
    if user_input:
        with st.spinner("Agent is thinking..."):
            # Helper to run the async agent call in Streamlit's sync flow
            async def run_query():
                return await agent.ainvoke({"messages": [HumanMessage(content=user_input)]})
            
            result = asyncio.run(run_query())
            
            # Display final agent response in a formatted field
            st.subheader("Response:")
            st.info(result['messages'][-1].content)
    else:
        st.warning("Please enter a city name or question.")

async def main():
    user_query = "What is the weather in Indianapolis?"
    result = agent.invoke({"messages": [HumanMessage(content=user_query)]})

    print(f"User Query: {user_query}")
    print(f"Agent Response: {result['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())
    #main()
