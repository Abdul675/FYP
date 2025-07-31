import json
from crewai import Crew
from utils.parsing import get_parser_agent_and_task
from agents.gmail_agent import get_gmail_task_and_agent
from agents.updated_calender import get_google_calendar_task_and_agent
from agents.drive_agent import get_drive_task_and_agent
# Add more agent/task imports if you extend support

  # Pydantic model for parsed output

def build_crew(user_input: str):
    print("🚀 Running Parser Crew...")
    parser_agent, parser_task = get_parser_agent_and_task(user_input)

    parsing_crew = Crew(
        agents=[parser_agent],
        tasks=[parser_task],
        manager_llm=None
    )

    crew_output = parsing_crew.kickoff()
    print(f"🔍 Raw crew_output: {crew_output}")

    try:
        parsed = getattr(crew_output, "pydantic", None)
        if parsed is None:
            raise ValueError("❌ crew_output.pydantic is missing.")

        # Access fields from parsed pydantic object
        service = parsed.target_service
        action = parsed.event_type
        print(f"✅ Parsed Service: {service}, Action: {action}")

        # Extract all fields as a dictionary
        data = parsed.dict()
        print(f"📦 Parsed Data: {data}")

    except Exception as e:
        raise ValueError(f"❌ Failed to access fields: {e}\nFull crew_output: {crew_output}")

    # Build agent + task based on the target service
    raw_service = parsed.target_service or ""
    service = raw_service.strip().lower()
    print(f"🧪 Raw service: '{parsed.target_service}' (type: {type(parsed.target_service)})")
    print(f"🧪 Normalized service: '{service}'")


    service_crew = None

    if service == "gmail":
        gmail_agent, gmail_task = get_gmail_task_and_agent({
            "recipient": data.get("recipient"),
            "subject": data.get("subject"),
            "body": data.get("body")
        })

        service_crew = Crew(
            agents=[gmail_agent],
            tasks=[gmail_task],
            manager_llm=None
        )

    elif service in ['google calendar','calendar']:
        action = data.get('event_type')
        calendar_agent, calendar_task = get_google_calendar_task_and_agent(action,{
            "summary": data.get("summary"),
            "start_datetime": data.get("start_datetime"),
            "event_duration_hour": data.get("event_duration_hour"),
            "event_duration_minutes": data.get("event_duration_minutes"),
            'attendees' : data.get('attendees'),
            'create_meeting_room' : data.get ('create_meeting_room')

        })
        service_crew = Crew(
            agents=[calendar_agent],
            tasks=[calendar_task],
            manager_llm=None
        )
        
    elif service in ['google drive','drive']:
        action = data.get('event_type')
        drive_agent, drive_task = get_drive_task_and_agent(action, {
            'file_to_upload' : data.get('file_to_upload'),
            'folder_to_upload_to': data.get('folder_to_upload_to'),
            'name_contains'     : data.get('name_contains'),
            'event_type' : data.get('event_type'),
            'name_exact' : data.get('name_exact')
            
        
        })

        service_crew = Crew(
            agents=[drive_agent],
            tasks=[drive_task],
            manager_llm=None
        )

    else:
        raise ValueError(f"❌ Unsupported service: {service}")

    print("🤖 Dispatching to Service Crew...")
    result = service_crew.kickoff()
    return result
