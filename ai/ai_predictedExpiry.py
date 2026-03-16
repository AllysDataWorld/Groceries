import json
import os
import asyncio
from app import app
from config import Config
app.config.from_object(Config)

def ai_predictedExpiry():
    """Run the agent and read its response"""

    # Import and execute the agent
    from ai.agent_main import run_agent_query
    asyncio.run(run_agent_query())  # This blocks until the agent finishes

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

        # ai_answer = response[0]['content']['parts'][0]['text']

        # Find classify_findings in the response
        classify_text = None
        for event in response:
            state = event.get("actions", {}).get("state_delta", {})
            if "classify_findings" in state:
                classify_text = state["classify_findings"]
                print("RAW classify_text:", repr(classify_text[:300]))  # repr shows whitespace/newlines clearly
                break

        if not classify_text.strip():
            return None, "ERR: classify_findings is empty"

        try:
            table_data = json.loads(classify_text.strip())
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
                return table_data, None
            return None, f"ERR: Could not parse response.\nRaw: {classify_text[:300]}"

    except Exception as ex:
        print(f"EXCEPTION occurred in {__file__} parsing JSON: {ex}")  # No JSON dump
        return None, f"EXCEPTION occurred in {__file__} parsing JSON: {ex}"

#unit test
# FILE = '\\ai_response_hello_world_agent_2026-02-16_11-46-51.json'
# FILE = '\\ai_response.json'
# PATH = r"C:\Users\after\OneDrive\Desktop\code_from_HD\Groceries\Groceries\FLASK\final_versions\v12_newenv\output\out_ai"
# temp = PATH+FILE
# ans, err = ai_predictedExpiry()
# print(ans)
