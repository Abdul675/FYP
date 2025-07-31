import json
from crewai import Crew
from utils.parsing import get_parser_agent_and_task
from agents.gmail_agent import get_gmail_task_and_agent
from agents.updated_calender import get_google_calendar_task_and_agent
from agents.drive_agent import get_drive_task_and_agent
from agents.genera_chat import fallback_response


def build_crew(user_input: str):
    print("🚀 Running Parser Crew...")

    try:
        # 1. Run parser agent
        parser_agent, parser_task = get_parser_agent_and_task(user_input)
        parsing_crew = Crew(agents=[parser_agent], tasks=[parser_task], manager_llm=None)
        crew_output = parsing_crew.kickoff()
        print(f"🔍 Raw crew_output: {crew_output}")

        # 2. Try to parse output
        parsed = getattr(crew_output, "pydantic", None)
        if parsed is None:
            raise ValueError("❌ crew_output.pydantic is missing.")

        data = parsed.dict()
        service = (parsed.target_service or "").strip().lower()
        action = data.get("event_type")
        print(f"✅ Parsed Service: {service}, Action: {action}")
        print(f"📦 Parsed Data: {data}")

        # 3. Dispatch to service-specific agent
        if service == "gmail":
            agent, task = get_gmail_task_and_agent({
                "recipient": data.get("recipient"),
                "subject": data.get("subject"),
                "body": data.get("body")
            })
        elif service in ["google calendar", "calendar"]:
            agent, task = get_google_calendar_task_and_agent(action, {
                "summary": data.get("summary"),
                "start_datetime": data.get("start_datetime"),
                "event_duration_hour": data.get("event_duration_hour"),
                "event_duration_minutes": data.get("event_duration_minutes"),
                "attendees": data.get("attendees"),
                "create_meeting_room": data.get("create_meeting_room"),
                'time_min': data.get("time_min"),
                'time_max': data.get("time_max"),
                'timezone': data.get("timezone")
            })
        elif service in ["google drive", "drive"]:
            agent, task = get_drive_task_and_agent(action, {
                "file_to_upload": data.get("file_to_upload"),
                "folder_to_upload_to": data.get("folder_to_upload_to"),
                "name_contains": data.get("name_contains"),
                "name_exact": data.get("name_exact"),
                "event_type": action
            })
        else:
            # 🔁 Trigger fallback if unknown service
            print("❌ Unsupported service. Fallback triggered.")
            return fallback_response(user_input)

        # 4. Run service-specific crew
        print("🤖 Dispatching to Service Crew...")
        service_crew = Crew(agents=[agent], tasks=[task], manager_llm=None)
        result = service_crew.kickoff()

        # ✅ Return final result
        return getattr(result, "final_answer", str(result))

    except Exception as e:
        print("❌ Error in dispatcher:", e)
        return fallback_response(user_input)
