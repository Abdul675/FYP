# agents/parser_agent.py
from composio_crewai import Action
from crewai import Agent, Task
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional , List
import datetime as DT
from common.openai_config import get_openai_model
from crewai import Agent, Task,Crew
from common.composio_setup import get_tools_for_actions

tools = get_tools_for_actions([
    Action.GOOGLECALENDAR_GET_CURRENT_DATE_TIME
    
])
# getting required tools from composio for this agent
class date_parser(BaseModel):
    timezone: int = Field(description="5")
    
    

# pydantic class for parsing agent 
class ParsedAction(BaseModel):
    event_type: str = Field(description="The type of action to perform, e.g., send_email, create_event, list_events, find_event, delete_event, upload a file, create_doc, update_sheet")
    target_service: str = Field(description="The Google product involved, e.g., gmail, calendar, drive, meet, sheets")

    # Gmail
    recipient: Optional[str] = Field(default=None, description="Recipient email address")
    subject: Optional[str] = Field(default=None, description="Subject line of the email")
    body: Optional[str] = Field(default=None, description="Main content of the email")

    # Calendar
    summary: str = Field(description="Title of the event")
    start_datetime: str = Field(description="Start time in format like '5:30, 3:00 PM' or '2024-03-20T15:00:00Z'")
    event_duration_hour: int = Field(description="Duration in hours (0-24)", ge=0, le=24)
    event_duration_minutes: int = Field(description="Duration in minutes (0-59)", ge=0, le=59)
    attendees: List[str] = Field(description="List of attendee email addresses")
    description: Optional[str] = Field(description="Event description", default=None)
    calendar_id: Optional[str] = Field(description="Calendar ID, usually 'primary'", default="primary")
    timezone: Optional[str] = Field(description="IANA timezone Asia/Karachi", default=None)
    create_meeting_room: Optional[bool] = Field(description="Whether to create Google Meet", default=True)
    send_updates: Optional[bool] = Field(description="Whether to send updates to attendees", default=True)
    time_min: Optional[str] = Field(description="Start time for finding free slots", default=None)
    time_max: Optional[str] = Field(description="End time for finding free slots", default=None)
    # Sheets
    sheet_action: Optional[str] = Field(default=None, description="Action to perform on Google Sheets: read, write, update")
    sheet_data: Optional[str] = Field(default=None, description="Data to write or update in the sheet")
    sheet_name: Optional[str] = Field(default=None, description="Name of the sheet or tab")

    # Drive / Docs
    name_contains: str = Field(description="Search for folders with a name contaning specific words. Case-insensitive")
    name_exact: Optional[str] = Field(default=None, description="Exact name of the folder to search for")
    folder_to_upload_to : str = Field(description='Name of the folder where file will be uploaded')
    file_to_upload: Optional[str] = Field(default=None, description="The path of file which will be uploaded")
    action_type: Optional[str] = Field(default=None, description="Action like create, read, delete")

    # Meet
    meeting_title: Optional[str] = Field(default=None, description="Title or topic of the meeting")
    meeting_time: Optional[str] = Field(default=None, description="Scheduled time for the meeting")

# Pydantic for gmail 

date_agent = Agent(
    role="Date and Time Parser",
    goal="Extract and format date and time information from user input",
    backstory="""You're responsible for interpreting date and time information from natural language input.""",
    llm = get_openai_model(),
    tools = tools
)

def get_parser_agent_and_task(user_input: str):
    llm = get_openai_model()

    parser_agent = Agent(
        role="Google Workspace Parser Agent",
        goal="Understand user's natural language input and extract structured data for actions across Google services",
        backstory="""
            You're responsible for interpreting user intent for automating tasks across Gmail, Google Calendar, Google Sheets,
            Google Drive, and Google Meet. You extract clear structured information from natural input and hand it off to specialized agents.
        """,
        llm=llm,
        verbose=True,
    )
    date_task = Task(
    description=f"""
       Your task is to extract and resolve date and time from {user_input} like 'next Friday at 11pm'.
       You must convert expressions like 'tomorrow', 'next Monday', or 'in 2 days' into full datetime format.
       Use timezone offset (e.g., UTC+5 for Pakistan) when necessary.
    """,
    agent=date_agent,  # Define a simple Pydantic for datetime output
    expected_output="""
       Return datetime in ISO format (e.g., '2025-05-18T23:00:00+05:00') based on current date and input expression.
    """
)
    
    crew = Crew(
                agents=[date_agent],
                tasks=[date_task],
            )
    date_recieved = crew.kickoff()
    print(f"Date Recieved: {date_recieved}")
        # Delete event description

    parse_input_task = Task(
        description=f"""     
Your task is to identify the Google service the user wants to interact with (e.g., Gmail, Google Calendar, Google Meet, Google Sheets, or Google Drive) and extract the relevant information in a structured format.

Some user inputs may be incomplete or ambiguous, especially due to voice commands. In such cases, you should only extract the information that is clear and relevant.

✉️ Gmail
For Gmail-related inputs, extract the following:

Recipient email address: If the user provides an incomplete or informal input like a name ("khan shabir gulam") or just a username ("khanhanifutp"), complete it using standard format (e.g., "khanshabirgulam@gmail.com", "khanhanifutp@gmail.com").

Subject (if specified)

Body content

📅 Google Calendar
For Calendar-related actions, extract the following from {user_input} and {date_recieved}:

action: one of the following — create_event, find_event, delete_event, update_event, list_events, find_free_slots

summary: Title of the event

start_datetime: Full datetime in the format 'YYYY-MM-DDTHH:MM:SS' (e.g., '2025-01-16T13:00:00')

Use {date_recieved} when the user input includes relative terms like "tomorrow", "next Friday", etc.

event_duration_hour: Integer from 0 to 24

event_duration_minutes: Integer from 0 to 59

attendees: List of valid email addresses

description: (Optional) Description of the event

create_meeting_room: Boolean (default True)

send_updates: Boolean (default True)

calendar_id: Optional (default 'primary')

timezone: Always use IANA timezone format (e.g., 'Asia/Karachi')


        User input: "{user_input}"
        """,
        agent=parser_agent,
        output_pydantic=ParsedAction,
        expected_output="""
A structured object with:
- service: Identified Google service
- action: Specific action to perform 
- data: Service-specific information extracted from input
- missing_info: Critical information that's missing (if any)

"""
    )

    return parser_agent, parse_input_task

