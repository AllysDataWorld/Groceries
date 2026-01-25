import os
import datetime
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scopes required for accessing the user's calendar (read/write access)
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
TOKEN_PATH = r"C:\Users\after\OneDrive\Desktop\code_from_HD\Groceries\Groceries\FLASK\final_versions\v12_newenv\ai\AskedGoogleGemini\"
TOKEN_FILE = 'client_secret_774480924598-m1qdfg42c5td05c9kdsoflc91mli4rdi.apps.googleusercontent.com.json'  # File to store the user's access and refresh tokens
TOKEN_FILE = TOKEN_PATH + TOKEN_FILE 

def get_google_calendar_service(TOKEN_FILE):
    """
    Handles the authentication process using OAuth 2.0 (Installed App Flow).
    The user's credentials are saved locally in token.json after the first successful authentication.
    """
    creds = None
    
    # 1. Check for existing token
    if os.path.exists(TOKEN_FILE):
        print("Loading existing credentials from token.json...")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # 2. Refresh or authorize if credentials are missing or expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Credentials expired. Attempting to refresh...")
            creds.refresh(Request())
        else:
            # Requires the user to manually complete the OAuth flow in a browser
            print("Authorization required. Opening browser for user consent...")
            # NOTE: You MUST download your credentials.json file from Google Cloud Console
            # and place it in the same directory as this script.
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("\n--- AUTH ERROR ---")
                print("FATAL: 'credentials.json' file not found.")
                print("Please download your OAuth 2.0 Client ID JSON from Google Cloud Console and save it as 'credentials.json'.")
                return None
            except Exception as e:
                print(f"\n--- AUTH ERROR --- \nAn error occurred during OAuth flow: {e}")
                return None

        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print("New credentials saved to token.json.")

    # Build and return the Google Calendar service object
    try:
        service = build('calendar', 'v3', credentials=creds)
        print("Google Calendar Service successfully initialized.")
        return service
    except Exception as e:
        print(f"Error building service: {e}")
        return None

def create_calendar_event(service, event_data):
    """
    Agent 2's core function: Creates an event in the user's primary Google Calendar.

    Args:
        service: The authenticated Google Calendar API service object.
        event_data: The structured JSON payload from the previous agent.
    """
    if not service:
        print("Cannot create event: Calendar service is unavailable.")
        return

    # The Google Calendar API expects the event body to be structured exactly like event_data.
    event = event_data
    calendar_id = 'primary'  # Use the user's primary calendar

    print(f"\nAttempting to create event: {event.get('summary', 'Untitled Event')}")
    print("-" * 30)

    try:
        # Call the API to insert the event
        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        print("✅ SUCCESS: Event created.")
        print(f"  Event ID: {event_result.get('id')}")
        print(f"  Summary: {event_result.get('summary')}")
        print(f"  Status: {event_result.get('status')}")
        print(f"  View Link: {event_result.get('htmlLink')}")

    except HttpError as error:
        print(f"❌ ERROR: An API error occurred during event creation: {error}")
    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred: {e}")


# --- Agent Workflow Simulation ---

if __name__ == '__main__':
    
    # -------------------------------------------------------------------------
    # SIMULATION OF AGENT 1 OUTPUT
    # This is the structured data that the first agent extracts from raw text.
    # -------------------------------------------------------------------------
    
    # Example raw user request: "Schedule a Q4 strategy meeting next Monday from 3:00 to 4:30 PM with Alice and Bob in Chicago."
    # Agent 1 (LLM with structured output) generates this JSON:
    
    AGENT_1_OUTPUT = {
        'summary': 'Q4 Strategy Session',
        'location': 'Virtual Meeting Room',
        'description': 'Review Q3 performance and define key objectives for Q4.',
        # Dates and Times MUST be in RFC3339 format (YYYY-MM-DDThh:mm:ss±hh:mm)
        'start': {
            'dateTime': '2025-12-08T15:00:00', # Assuming Dec 8 is next Monday
            'timeZone': 'America/Chicago',
        },
        'end': {
            'dateTime': '2025-12-08T16:30:00',
            'timeZone': 'America/Chicago',
        },
        'attendees': [
            {'email': 'alice@example.com'},
            {'email': 'bob@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60}, # 1 day before
                {'method': 'popup', 'minutes': 15},     # 15 minutes before
            ],
        },
    }

    print("--- Calendar Agent Initializing ---")
    print(f"Simulated Input from Agent 1 (Structured Event Data):\n{json.dumps(AGENT_1_OUTPUT, indent=2)}")

    # -------------------------------------------------------------------------
    # AGENT 2 CORE LOGIC EXECUTION
    # -------------------------------------------------------------------------
    
    # 1. Get the authenticated service
    calendar_service = get_google_calendar_service()

    # 2. Pass the service and the structured data to the creation function
    if calendar_service:
        create_calendar_event(calendar_service, AGENT_1_OUTPUT)
    
    print("\n--- Agent Workflow Complete ---")