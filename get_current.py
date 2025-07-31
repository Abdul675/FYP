    
 # agents/parser_agent.py
from composio_crewai import Action
from crewai import Agent, Task
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional , List
import datetime as DT
from common.openai_config import get_openai_model
from crewai import Agent, Task,Crew
from common.composio_setup import get_tools_for_actions

user_input = "tomorrow at 5pm"

tools = get_tools_for_actions([
    Action.GOOGLECALENDAR_GET_CURRENT_DATE_TIME
    
])
# getting required tools from composio for this agent
class date_parser(BaseModel):
    timezone: int = Field(description="The timezone offset from UTC to retrieve current date and time, like for location of UTC+6, you give 6, for UTC -9, your give -9.")
    
    
    
date_agent = Agent(
    role="Date and Time Parser",
    goal="Extract and format date and time information from user input",
    backstory="""You're responsible for interpreting date and time information from natural language input.""",
    llm = get_openai_model(),
    tools = tools
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