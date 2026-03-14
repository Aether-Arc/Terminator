import json
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OLLAMA_BASE_URL, OPENAI_API_KEY, LOCAL_MODEL
from tools.system_tools import swarm_tools
from ml_models.engagement_predictor import EngagementPredictor
from config import get_resilient_llm

class MarketingAgent:
    def __init__(self):
        # Temperature 0.4 allows for creative copywriting while remaining factual
        self.llm = get_resilient_llm(temperature=0.4)
        self.predictor = EngagementPredictor()
        # 🚀 Bind the internet search tools to the marketing agent
        self.agent_executor = create_react_agent(self.llm, swarm_tools)

    async def generate_campaign(self, event_data, specifics):
        event_name = event_data.get('name', 'the upcoming event')
        # Extract broader context so the AI knows WHAT the event actually is
        event_theme = event_data.get('event_type', 'General Event')
        event_constraints = event_data.get('user_constraints', 'No specific constraints.')
        days_until = event_data.get('days_until_event', 14)
        
        prediction = self.predictor.predict_best_time(days_until)
        best_time = prediction.get("recommended_post_hour", "12:00")
        expected_score = prediction.get("expected_engagement_score", 0)

        prompt = f"""
You are an elite Event Marketing Director and Copywriter.

Create a viral campaign for:

Event: {event_name}

===============================
EVENT CONTEXT
===============================

Name: {event_name}
Type: {event_theme}
Constraints: {event_constraints}
Days until event: {days_until}

Task:
{specifics}

===============================
MANDATORY WEB RESEARCH LOOP
===============================

You MUST use web_search.

Follow this loop:

1. Read event theme
2. Read constraints
3. Search related news
4. Search industry trends
5. Search event marketing ideas
6. Use results in copy

Allowed searches:

"{event_theme} news"
"{event_theme} trends 2025"
"{event_theme} event marketing ideas"
"{event_theme} latest breakthrough"
"{event_name} topic news"

DO NOT search generic trends.
DO NOT use celebrity gossip.
DO NOT use unrelated hashtags.

You must include at least ONE real trend.

===============================
EVENT-AWARE MARKETING
===============================

Content must match event.

Tech fest → innovation / AI / startup
Cultural fest → art / music / dance
Social fest → fun / campus / games
Workshop → learning / skills
Seminar → knowledge / speakers
Sports → competition
Music → concert / vibe

Never mix domains.

===============================
SCHEDULE AWARENESS
===============================

If event has multiple days:
create hype campaign

If event soon:
urgent tone

If event far:
build-up tone

If short event:
focus on highlight

If big fest:
focus on experience

===============================
CAMPAIGN STRATEGY
===============================

First think:

Who is audience?
Why attend?
What is unique?
What is trending?
What emotion to trigger?

Then write copy.

===============================
PLATFORM STYLE
===============================

If task is post:
short + hype

If task is announcement:
formal + exciting

If task is campaign:
multiple lines

If task is reel:
catchy

If task is linkedin:
professional

===============================
ML DEPLOYMENT
===============================

Best posting time: {best_time}
Expected engagement: {expected_score}

Mention posting time ONLY as:

Internal Deployment Instruction

Do NOT put inside post.

===============================
COPY RULES
===============================

No hallucination.
No random trends.
No fake news.
No unrelated hashtags.
No generic text.

Make it sound real.

===============================
OUTPUT
===============================

Return only the campaign text.
At end add:

Internal Deployment Instruction:
Post at {best_time}
"""
        
        try:
            print(f"[*] MarketingAgent: Researching industry trends for {event_name}...")
            # 🚀 Execute through the ReAct agent so it can intelligently use the web_search tool
            response = await self.agent_executor.ainvoke({"messages": [("user", prompt)]})
            return response["messages"][-1].content
            
        except Exception as e:
            print(f"[🔥] MarketingAgent Error: {e}")
            return f"Error generating marketing copy: {e}"