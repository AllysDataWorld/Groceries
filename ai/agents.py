# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 09:28:07 2025

@author: after
"""
from my_agent import retry_config


from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool, FunctionTool, google_search



# Classify Agent: Its job is to classify items
classify_agent = Agent(
    name="ClassifyAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a specialized classification agent. When given a list of items, your only job is to classify the item into
    1) Perishable
    2) Pantry
    Your response should be 1 word""",
    tools=[google_search],
    output_key="classify_findings",  # The result of this agent will be stored in the session state with this key.
)




# Research Agent: Its job is to use the google_search tool and present findings.
research_agent = Agent(
    name="ResearchAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a specialized research agent. Your only job is to use the
    google_search tool to find out how long a fruit or vegatable lasts in the fridge. 
    Your response should always be the number of weeks, and should a number""",
    tools=[google_search],
    output_key="research_findings",  # The result of this agent will be stored in the session state with this key.
)





# Calendar Agent: Its job is to classify items
Calendar_agent = Agent(
    name="CalendarAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a specialized Calendar agent. Your only job is to use the google calendar tool to create a calender entry for the duration for each perishable item is expected to last.
    Your response is only done, or not done""",
    #tools=[google_calender],
    output_key="Calendar_findings",  # The result of this agent will be stored in the session state with this key.
)


