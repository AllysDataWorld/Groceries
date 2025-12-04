# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 11:38:57 2025

@author: after
"""


#from ai.agents import agents
import utils as uts
from ai.my_agent import retry_config

from app import app
import os 
import csv

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
#from google.adk.responses import AgentResponse # You may need this import
from google.adk.tools import AgentTool, FunctionTool, google_search

import asyncio
from google.adk.runners import InMemoryRunner # or your specific runner


# Get List Agent: Get the list of uploaded items
get_list_agent = Agent(
    name="get_list_agent",
    model=Gemini(
        model= "gemini-2.5-flash-lite", # <== wants me to change to "gemini-2.5-flash",
        retry_options=retry_config
    ),
    description = "You can only use the tools available",
    instruction="""You only job is to call uts.get_upload_items() and return ONLY the raw data 
                                   (the list of items and the upload date) as a single, clean JSON object. 
                                   Do NOT include any descriptive sentences or commentary in your final output.""",
    tools = [uts.get_upload_items],
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
                    2) for each item in the list, classify the item as perishable or nonperishable item.
                    3) for each item that is perishable, get an estimated number of weeks the item will last.
                    Your response should be a dictionary containing only be the item, your classification, and the estimated number of weeks.
                    You can use the google search tool if needed for the classification.
                    You must use the google search tool for the number of weeks estimation.
                    If you dont know, then classify the item as IDK, and the estimated number of weeks as 99.
                    """,
    tools = [google_search],
    output_key="classify_findings",  # The result of this agent will be stored in the session state with this key.

)
    
    
from google.adk.agents import Agent, SequentialAgent
combined_flow = SequentialAgent(
    name="Groceries_Classifier_Flow",
    sub_agents=[get_list_agent, classifyagent],
)

    
# from google.adk.flows import AgentFlow   #import didn't work
# combined_flow = AgentFlow(
#     name="Groceries_Classifier_Flow",
#     agents=[
#         get_list_agent,
#         classifyagent 
#     ],
#     # You may need an instruction for the flow itself
#     instruction="Execute the first agent to get the list, then execute the second agent to classify the items.",
#     output_key="final_classification"    
#  )


my_prompt = "what is your classification for the list of items"

runner = InMemoryRunner(agent=combined_flow)

# Define an async function to contain the await call


async def run_agent_query():
    # The await keyword must be inside an async function
    response = await runner.run_debug(my_prompt)
    print(response)
    write_resp = os.path.join(app.config['OUTPUT_FOLDER'], 'ai_response.txt')
    with open(write_resp, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(response)
    
# Run the async function using asyncio
if __name__ == "__main__":
    asyncio.run(run_agent_query())
    print("✅ Agent Query Done.")
    
    
    
    
# # Root Coordinator: Orchestrates the workflow by calling the sub-agents as tools.
# root_agent = Agent(
#     name="Coordinator",
#     model=Gemini(
#         model="gemini-2.5-flash-lite",
#         retry_options=retry_config
#     ),
#     # This instruction tells the root agent HOW to use its tools (which are the other agents).
#     description = "You are a coordinator of two agents.",
#     instruction="""Your goal is receive a dictionary.
#     1. First, you MUST call the `get_list_agent` tool to get a list of items, and the date.
#     2. Next, you MUST call the `classifyagent` tool to receive dictionary of the item, its category, and an estimated number of weeks.
#     3. Finally, present the information clearly to the user as your response.""",
#     # We wrap the sub-agents in `AgentTool` to make them callable tools for the root agent.
#     tools=[AgentTool(get_list_agent), AgentTool(classifyagent)],
# )

# print("✅ root_agent created.")
    
    




