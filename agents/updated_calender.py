from common.composio_setup import get_tools_for_actions
from common.openai_config import get_openai_model
from composio_crewai import Action
from crewai import Agent, Task,Crew
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta

# getting required tools from composio for this agent
llm = get_openai_model()

tools = get_tools_for_actions([
    Action.GOOGLECALENDAR_CREATE_EVENT,
    Action.GOOGLECALENDAR_FIND_EVENT,
    Action.GOOGLECALENDAR_DELETE_EVENT,
    Action.GOOGLECALENDAR_FIND_FREE_SLOTS,
    Action.GOOGLECALENDAR_UPDATE_EVENT,
    Action.GOOGLECALENDAR_LIST_CALENDARS
])

# Pydantic class for Google Calendar Event
class CalendarEventRequest(BaseModel):
    summary: str = Field(..., description="The title of the event")
    start_datetime: str = Field(..., description="Start time in ISO 8601 format (e.g., '2025-05-10T15:00:00')")
    event_duration_hour: int = Field(..., description="Event duration in hours (0-24)", ge=0, le=24)
    event_duration_minutes: int = Field(..., description="Event duration in minutes (0-59)", ge=0, le=59)
    attendees: Optional[List[str]] = Field(None, description="List of attendee email addresses")
    calendar_id: Optional[str] = Field("primary", description="Calendar ID, usually 'primary'")
    timezone: Optional[str] = Field(None, description=" 'Asia/Karachi'")
    description: Optional[str] = Field(None, description="Description of the event")
    create_meeting_room: Optional[bool] = Field(True, description="Whether to create a Google Meet link for the event")
    send_updates: Optional[bool] = Field(True, description="Whether to send updates to attendees")
    query : Optional[str] = Field(None, description="Search term to find events that match these terms in the event's summary, description, location, attendee's displayName, attendee's email, organizer's displayName, organizer's email, etc if needed")
    time_min: Optional[str] = Field(None, description="Start time for finding free slots")
    time_max: Optional[str] = Field(None, description="End time for finding free slots")

# Google Calendar Agent
calendar_agent = Agent(
    role="Google Calendar Assistant",
    goal="""Manage and organize events in the user's Google Calendar, including creation, update, deletion, and free slot discovery.""",
    backstory="""You are an assistant specializing in Google Calendar management. You handle creating events, finding events, 
                 updating events, checking for free slots, and deleting events based on user input.""",
    llm=llm,
    verbose=True,
    tools=tools  # Composio tools for Google Calendar
)

def get_google_calendar_task_and_agent(action: str, data: dict) -> tuple[Agent, Task]:
    """
    Function that dynamically generates a task for Google Calendar actions such as create, update, delete, find event, and find free slots.
    The task will be defined based on the action and the data passed.
    """
    # Validate the input data using Pydantic model
    input_data = CalendarEventRequest(**data)

    # Initialize the task description
    description = ""
    
    # Based on the action, we define the task description
    if action == "create_event":
        # Create event description
        start_time = datetime.strptime(input_data.start_datetime, "%Y-%m-%dT%H:%M:%S")
        end_time = start_time + timedelta(hours=input_data.event_duration_hour, minutes=input_data.event_duration_minutes)
        description = f"""
        Create a new calendar event titled '{input_data.summary}' from {start_time} to {end_time}.
        Attendees: {input_data.attendees}
        Description: {input_data.description if input_data.description else "No description provided"}
        Meeting Room: {'Yes' if input_data.create_meeting_room else 'No'}
        Send Updates: {'Yes' if input_data.send_updates else 'No'}
        timezone: {input_data.timezone if input_data.timezone else "No timezone provided"}
        """
    
    elif action == "find_event":
        # Find event description
        description = f"Find an event that matches '{input_data.query}' or {input_data.summary} in the calendar with ID '{input_data.calendar_id}'."
    
    elif action == "delete_event":
        
        folder_id_task = Task(
                description=f"Find folder that matches with the {input_data.summary} or {input_data.query} in Google Calendar.",
                agent=calendar_agent,
                expected_output="only event_id of the found event."
            )
        crew = Crew(
                agents=[calendar_agent],
                tasks=[folder_id_task]
            )
        event_id = crew.kickoff()
        # Delete event description
        
        description = f"Delete an event located at this {event_id} with ID '{input_data.calendar_id}'."
    
    elif action == "find_free_slots":
        

         start_time = datetime.strptime(input_data.time_min, "%Y-%m-%dT%H:%M:%S")
         end_time = datetime.strptime(input_data.time_max, "%Y-%m-%dT%H:%M:%S")
         description = f"Find free slots between {start_time} and {end_time}."
    
    elif action == "update_event":
        
        folder_id_task = Task(
                description=f"Find folder that matches with the {input_data.summary} or {input_data.query} in Google Calendar.",
                agent=calendar_agent,
                expected_output="only event_id of the found event."
            )
        crew = Crew(
                agents=[calendar_agent],
                tasks=[folder_id_task]
            )
        event_id = crew.kickoff()
        # Update event description
        start_time = datetime.strptime(input_data.start_datetime, "%Y-%m-%dT%H:%M:%S")
        end_time = start_time + timedelta(hours=input_data.event_duration_hour, minutes=input_data.event_duration_minutes)
        description = f"Update the {event_id} with new time: from {start_time} to {end_time} and updated attendees {input_data.attendees} "

    # Create the task object
    calendar_task = Task(
        description=description,
        agent=calendar_agent,
        expected_output=""" Confirmation message that the event has been created/updated/deleted successfully.
        If the action is to find free slots, return a list of available time slots.
    """
    )

    return calendar_agent, calendar_task

# Example usage for creating an event:
