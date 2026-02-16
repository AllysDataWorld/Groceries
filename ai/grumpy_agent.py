# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 11:38:57 2025

@author: after
here
"""

from ai.testing.my_agent import retry_config
from datetime import datetime
import json
import os
import time
from app import app

from config import Config
app.config.from_object(Config)

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini

import asyncio
from google.adk.runners import InMemoryRunner # or your specific runner

start_grumpy = time.time()
# Get List Agent: Get the list of uploaded items
hello_world_agent = Agent(
    name="hello_world_agent",
    model=Gemini(
        model= "gemini-2.5-flash-lite", # <== wants me to change to "gemini-2.5-flash",
        retry_options=retry_config
    ),
    description = "you are grumpy",
    instruction= 'respond with one sentence and be annoyed'
)

my_prompt = "Hello"

runner = InMemoryRunner(agent=hello_world_agent)

# start_grumpy = 0
# start_run_agent = 0
# start_dump = 0
# start_googlecode = 0
# start_google_ifs = 0

# Define an async function to contain the await call
async def run_agent_query():
    start_run_agent = time.time()
    response = await runner.run_debug(my_prompt) # The await keyword must be inside an async function
    print("\ntype: ", type(response))
    print(response)

    dt = (datetime.today().strftime('%Y-%m-%d_%H-%M-%S'))
    response_file = f"ai_response_hello_world_agent_{dt}.json"
    json_path = os.path.join(app.config['OUT_AI'], response_file)

    print(f"\n{"-"*10}\nresponse   : TYPE:{type(response)}" )
    print(f"response[0]: TYPE:{type(response[0])}\n{"-"*10}" ) #TYPE:<class 'google.adk.events.event.Event'>

    start_dump = time.time()
    try:
        with open(json_path, "w") as f:
            json.dump([e.model_dump() for e in response], f, indent=2)
        print("\nCompleted Dump @", json_path)
    except:
        print("EXCEPTION occured while creating json dump file")

    start_googlecode = time.time()
    print(f"\n{"-"*10}\nLook through variables")
    event = response[0]
    try:
        print('look for type')
        print("type:", event.type)
    except:
        try:
            print('look for author')
            print("author:", event.author)
        except:
            try:
                print('look for content')
                print("content:", event.content)
            except:
                try:
                    print('look for action')
                    print("action:", event.actions)
                except:
                    print('Didnt find anything')

    start_google_ifs = time.time()
    print(f"\n{"-"*10}\nCODE FORM GOOGLE SDK")

    if event.content and event.content.parts:
        if event.get_function_calls():
            print("  Type: Tool Call Request")
        elif event.get_function_responses():
            print("  Type: Tool Result")
        elif event.content.parts[0].text:
            if event.partial:
                print("  Type: Streaming Text Chunk")
            else:
                print("  Type: Complete Text Message")
        else:
            print("  Type: Other Content (e.g., code result)")
    elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
        print("  Type: State/Artifact Update")
    else:
        print("  Type: Control Signal or Other")
    #
    # end = time.time()
    #
    # print(type(start_grumpy), " st")
    # print(type(start_run_agent), " ag")
    # print(type(start_dump), " d")
    # print(type(start_googlecode), " gc")
    # print(type(start_google_ifs), " gi")
    #
    # print(f"start_grumpy:{int(end - start_grumpy)} seconds)")
    # print(f"start_run_agent:{end - start_run_agent}")
    # print(f"start_dump:{end - start_dump}")
    # print(f"start_googlecode:{end - start_googlecode}")
    # print(f"start_google_ifs:{end - start_google_ifs}")


# Run the async function using asyncio
if __name__ == "__main__":
    asyncio.run(run_agent_query())
    print("✅ Agent Query Done.")
