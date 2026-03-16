# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 11:38:57 2025

@author: after
here
"""


#from ai.agents import agents
import utils as uts
from google.genai import types
from utils import get_upload_items_for_AI
from datetime import datetime
from app import app
import os 
import csv
import json
import time
#from parse_ai_response import show_python_code_and_result

from config import Config
app.config.from_object(Config)

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.adk.models.google_llm import _ResourceExhaustedError
#from google.adk.responses import AgentResponse # You may need this import

import asyncio
from google.adk.runners import InMemoryRunner # or your specific runner


#from ai.testing.my_agent import retry_config
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

# Get List Agent: Get the list of uploaded items
get_list_agent = Agent(
    name="get_list_agent",
    model=Gemini(
        model= "gemini-2.5-flash-lite", # <== wants me to change to "gemini-2.5-flash",
        retry_options=retry_config
    ),
    description = "You can only use the tools available",
    instruction="""You only job is to call get_upload_items_for_AI() and return ONLY the raw data 
                                   (the list of items and the upload date) as a single, clean JSON object. 
                                   Do NOT include any descriptive sentences or commentary in your final output.""",
    tools = [get_upload_items_for_AI],
    output_key="Items_Bought",  # The result of this agent will be stored in the session state with this key.
)

# Classify Agent: Its job is to classify items
classifyagent = Agent(
    name="classifyagent",
    model=Gemini(
        model="gemini-2.5-flash-lite", # <== wants me to change to "gemini-2.5-flash",
        retry_options=retry_config
    ),
    description = "You are a highly accurate classification agent. If you dont know the answer, you will return IDK",
    instruction="""Your goal is to create a dictionary:
                    1) You must first get the the list of items from {Items_Bought},  
                    2) for each item in the list, classify the item as "perishable" or "non-perishable" or "semi-perishable" item.
                    3) for each item that is perishable, get an estimated number of weeks the item will last. Store this as EST_WEEKS (a number).
                    4) Get the upload_date from {Items_Bought} in the format '%Y/%m/%d' and calculate predicted_expiry_date by adding EST_WEEKS to it. 
                    Your response should be a dictionary containing only the following: item, your classification, upload_date, EST_WEEKS, predicted_expiry_date.
                    You can use the google search tool for the classification and EST_WEEKS.
                    If you dont know, then classify the item as IDK, and the estimated number of weeks as 99.
                    You MUST return ONLY a valid JSON array. No bullet points, no markdown, no explanation text.
                    Do NOT wrap the output in ```json``` code blocks.
                    
                    The output must follow this exact format:
                    [
                        {
                            "item": "Banana",
                            "classification": "perishable",
                            "upload_date": "2024/07/26",
                            "EST_WEEKS": 1,
                            "predicted_expiry_date": "2024/08/02"
                        },
                        {
                            "item": "Nuts",
                            "classification": "non-perishable",
                            "upload_date": "2024/07/26",
                            "EST_WEEKS": 99,
                            "predicted_expiry_date": "2026/07/24"
                        }
                    ]
                    """,
    tools = [google_search],
    output_key="classify_findings",  # The result of this agent will be stored in the session state with this key.
)
    
from google.adk.agents import SequentialAgent
combined_flow = SequentialAgent(
    name="Groceries_Classifier_Flow",
    sub_agents=[get_list_agent, classifyagent],
)
print("✅ Groceries_Classifier_Flow created.")

my_prompt = "get the classification for the list of items and then calculate the predicted_expiry_date for each item"

runner = InMemoryRunner(agent=combined_flow)

# Define an async function to contain the await call
async def run_agent_query():
    try:
        response = await runner.run_debug(my_prompt) # The await keyword must be inside an async function
        print("response created: type: ", type(response))

        json_path = os.path.join(app.config['OUT_AI'], app.config['AI_RESPONSE'])

        serializable = [e.model_dump() for e in response] #Think of response like a file handle — you can't dump the file handle itself, you have to read from it first.
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, default=lambda o: list(o) if isinstance(o, set) else str(o))

        # # The lambda version
        # default = lambda o: list(o) if isinstance(o, set) else str(o)
        #
        # # Is exactly the same as writing this:
        # def handle_unserializable(o):
        #     if isinstance(o, set):
        #         return list(o)  # convert set → list
        #     else:
        #         return str(o)  # convert anything else → string
        # json.dump(serializable, f, indent=2, default=handle_unserializable)

    except _ResourceExhaustedError as e:
        print(f"QUOTA EXCEEDED: {e}")
        # Write a structured error file so ai_predictedExpiry.py can handle it gracefully
        json_path = os.path.join(app.config['OUT_AI'], app.config['AI_RESPONSE'])
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"error": "quota_exceeded", "message": str(e)}, f, indent=2)



# Run the async function using asyncio
if __name__ == "__main__":
    start_main = time.time()
    asyncio.run(run_agent_query())
    end_main = time.time()
    duration = round(end_main - start_main, 2)
    print("Duration: ", duration)
    print("✅ Agent Query Done.")




