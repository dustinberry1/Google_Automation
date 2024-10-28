
#install in CLI
#pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib reportlab

#Go to the Google Cloud Console.
#Create a project.
#Enable the Google Calendar API.
#Create OAuth 2.0 credentials and download the credentials.json file.
#Store the credentials.json in your working directory.


#authentication and data pull

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import datetime

# Scopes for read access to Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_events():
    creds = None
    # Check if there are existing credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no credentials are available, let user authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Connect to the Google Calendar API
    service = build('calendar', 'v3', credentials=creds)
    
    # Set the time range for pulling data
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    return events


#pdf generation

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(events):
    pdf_filename = 'calendar_events.pdf'
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    
    # Title of the PDF
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 50, "Google Calendar Events Summary")
    
    # Table Headers
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 100, "Date")
    c.drawString(150, height - 100, "Time")
    c.drawString(250, height - 100, "Event")
    
    # Loop through events and write them to PDF
    c.setFont("Helvetica", 10)
    y_position = height - 120
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        end_time = event['end'].get('dateTime', event['end'].get('date'))
        event_summary = event.get('summary', 'No Title')
        
        # Date and Time Formatting
        event_date = start_time[:10]
        event_time = start_time[11:16] if 'T' in start_time else 'All Day'
        
        # Write data to PDF
        c.drawString(50, y_position, event_date)
        c.drawString(150, y_position, event_time)
        c.drawString(250, y_position, event_summary)
        
        y_position -= 20
        if y_position < 50:
            c.showPage()  # Start a new page if the content overflows
            y_position = height - 50
    
    c.save()
    print(f"PDF created: {pdf_filename}")

if __name__ == "__main__":
    events = get_calendar_events()
    create_pdf(events)


#Optional Enhancements
#Custom Templates: Use reportlab's Platypus module to create custom tables, graphics, and layouts.
#Error Handling: Add error handling for empty calendar data or missing fields.
#Automate Emailing: Use smtplib or a library like yagmail to email the generated PDF.
#Save Back to Calendar: Utilize Google Calendar API's events.update() method to attach the PDF as a URL or note in the event description.

#Schedule Automation
#You can schedule the script to run automatically using a task scheduler like cron (Linux/Mac) or Task Scheduler (Windows).