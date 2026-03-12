from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import datetime

# 1. LIVE INTERNET SEARCH TOOL
web_search = DuckDuckGoSearchRun(
    name="web_search",
    description="Search the live internet for current events, tech trends, news, or real-time data."
)

# 2. CALENDAR INTEGRATION TOOL
@tool
def check_calendar(date_string: str) -> str:
    """Checks the organizational calendar to see if key speakers or venues are available."""
    # In a real startup, you would connect the Google Calendar API here.
    # For the hackathon, we simulate the tool returning dynamic context.
    return f"Calendar Database checked for {date_string}: The Main Hall is available, but the requested Keynote Speaker is busy from 10 AM to 1 PM."

# 3. WEATHER API TOOL
@tool
def check_weather(location: str) -> str:
    """Checks the live weather forecast for the event location."""
    # In a real startup, you would hit the OpenWeather API here.
    return f"Live Weather for {location}: 80% chance of heavy thunderstorms and potential power outages."

# Export the tools array to be bound to the LLM
swarm_tools = [web_search, check_calendar, check_weather]