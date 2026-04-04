import json
import csv
import os
import asyncio
from app import app
from config import Config
app.config.from_object(Config)

def ai_predictedExpiry():
    """Run the agent and read its response"""

    print(f"--- UNCOMMITED OUT---> call AI")
    # Import and execute the agent: See Bug documented here: GIT_COMMITS:"AI SCOPE BUG" @ commit message: "FIXED AI BUG"
    # reload the module, then access the function from it
    import importlib
    import ai.agent_predictedExpiry as agent_module
    importlib.reload(agent_module)  # reloads the module
    asyncio.run(agent_module.run_agent_query())  # calls the fresh function. Also this blocks until the agent finishes

    # Now read the freshly written response file
    temp = os.path.join(app.config['OUT_AI'], app.config['AI_RESPONSE'])

    if not os.path.exists(temp) or os.path.getsize(temp) == 0:
        return None, "ERR: Agent failed to write output file"
    try:
        with open(temp, "r", encoding="utf-8") as f:
            response = json.load(f)

        # Check if agent wrote an error instead of results
        if isinstance(response, dict) and response.get("error") == "quota_exceeded":
            return None, "ERR: Google API quota exceeded — you've hit the free tier daily limit (20 requests). Try again tomorrow or upgrade your plan."

        # Find classify_findings in the response
        classify_text = None
        for event in response:
            state = event.get("actions", {}).get("state_delta", {})
            if "classify_findings" in state:
                classify_text = state["classify_findings"].strip()
                # print("RAW classify_text:", repr(classify_text[:300]))  # repr shows whitespace/newlines clearly
                break

        if not classify_text:
            return None, "ERR: classify_findings is empty"
        try:
            table_data = json.loads(classify_text)
            save_food_facts(table_data)
            return table_data, None

        # Agent returned markdown instead of JSON — extract with regex
        except json.JSONDecodeError:
            import re
            pattern = re.compile(
                r'\*\*(.+?):\*\*\s*([A-Za-z-]+)\.'  # colon is inside ** e.g. **Cereal:**
                r'.*?Upload Date:\s*([\d/]+)'
                r'.*?EST_WEEKS:\s*([\d.]+)'  # grabs first number, ignores "(months, approx...)"
                r'.*?Predicted Expiry Date:\s*([\d/]+)',
                re.DOTALL
            )
            bullets = re.split(r'\n\*+\s+', classify_text)
            table_data = []
            for b in bullets[1:]:  # skip the intro sentence
                m = pattern.search(b)
                if m:
                    item, classification, upload_date, est_weeks, expiry = m.groups()
                    table_data.append({
                        "item": item.strip(),
                        "classification": classification.strip(),
                        "upload_date": upload_date.strip(),
                        "EST_WEEKS": est_weeks.rstrip('.'),  # removes trailing dot e.g. "99."
                        "predicted_expiry_date": expiry.strip()
                    })
            if table_data:
                save_food_facts(table_data)
                return table_data, None
            return None, f"ERR: Could not parse response.\nRaw: {classify_text[:300]}"

    except Exception as ex:
        print(f"EXCEPTION occurred in {__file__} parsing JSON: {ex}")  # No JSON dump
        return None, f"EXCEPTION occurred in {__file__} parsing JSON: {ex}"


def save_food_facts(table):
    #EXPORT Food facts in two ways: a cumulating CSV and a small JSON DUMP with timestamp
    import pandas as pd
    if isinstance(table, list) and isinstance(table[0], dict):
        out_file = os.path.join(app.config['OUT_AI'], app.config['AI_FOOD_FACTS'])
        orig_df = pd.read_csv(out_file)
        df = pd.DataFrame()
        for row in table:
            tmp_df = pd.DataFrame(data=[row])
            df = pd.concat([tmp_df, df])
        df = pd.concat([orig_df, df])
        df.to_csv(out_file, index=0)
        print (f'Saved {out_file}')

    temp_dump = os.path.join(app.config['SAVE_DUMP'], app.config['AI_FOOD_FACTS_DUMP'])

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{temp_dump}_{timestamp}.json"

    from datetime import datetime
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(table, f) #TODO: add datetime to filename

    print (f'Saved {filename}')

    return None



#unit test
# FILE = '\\ai_response.json'
# PATH = r"C:\Users\after\OneDrive\Desktop\code_from_HD\Groceries\Groceries\FLASK\final_versions\v12_newenv\output\out_ai"
# temp = PATH+FILE
# with app.app_context():
#     ans, err = ai_predictedExpiry()
# print(ans)
