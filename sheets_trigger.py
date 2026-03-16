import os
import json
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv


load_dotenv()


def get_gspread_client():
    """
    Securely authenticates using the JSON string stored in the .env file.
    This prevents leaking 'service_account.json' on GitHub.
    """
    try:
        # 1. Grab the JSON string from environment variables
        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not creds_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not found in .env")

        # 2. Parse the string into a dictionary
        creds_dict = json.loads(creds_json)

        # 3. Define the scopes required for Google Sheets and Drive
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # 4. Authorize using the dictionary
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        print(f" Critical Error during Authentication: {e}")
        return None


def scan_sheet_and_trigger():
    """
    Polls the Google Sheet for new rows and POSTs them to the FastAPI endpoint.
    """
    client = get_gspread_client()
    if not client:
        return

    try:
        # Replace with the exact name of your Google Sheet
        sheet_name = os.getenv("GOOGLE_SHEET_NAME", "Book_Generation_Input")
        sheet = client.open(sheet_name).sheet1

        # Fetch all records as a list of dictionaries
        records = sheet.get_all_records()

        # Headers expected: Title, Notes, Status
        for i, row in enumerate(records, start=2):  # start=2 to account for header row
            title = row.get("Title")
            notes = row.get("Notes")
            status = row.get("Status")

            # Only process rows that haven't been 'Processed' yet
            if title and notes and status != "Processed":
                print(f"🚀 Found new project: '{title}'. Sending to Stage 1 API...")

                payload = {
                    "title": str(title),
                    "initial_notes": str(notes)
                }

                # Pointing to your FastAPI server (ensure it is running)
                api_url = "http://127.0.0.1:8000/projects/1-generate-outline"

                try:
                    response = requests.post(api_url, json=payload, timeout=10)

                    if response.status_code == 200:
                        # Assuming 'Status' is in Column C (3rd column)
                        sheet.update_cell(i, 3, "Processed")
                        print(f"✅ Successfully triggered workflow for: {title}")
                    else:
                        print(f"⚠️ API Error ({response.status_code}): {response.text}")

                except requests.exceptions.ConnectionError:
                    print(" Error: Could not connect to FastAPI. Is uvicorn running?")
                except Exception as e:
                    print(f" Request failed: {e}")

    except gspread.exceptions.SpreadsheetNotFound:
        print(f" Error: Could not find sheet named '{sheet_name}'. Check your .env")
    except Exception as e:
        print(f" Unexpected error scanning sheet: {e}")


if __name__ == "__main__":
    print("--- 🛰️ Google Sheets Polling Service Started ---")
    print("Press Ctrl+C to stop.")

    while True:
        scan_sheet_and_trigger()
        # Wait 30 seconds between scans to avoid Google API rate limits
        time.sleep(30)