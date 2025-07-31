from common.composio_setup import get_tools_for_actions
from common.openai_config import get_openai_model 
from composio_crewai import Action
from crewai import Agent, Task , Process
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional , List


# getting required tools from composio for this agent
llm = get_openai_model() 

tools = get_tools_for_actions([
    Action.GMAIL_CREATE_EMAIL_DRAFT,
    Action.GMAIL_SEND_EMAIL
])
#Pydantic class for gmail 

class EmailRequest(BaseModel):
    recipient: str = Field(..., description="The recipient's email address")
    subject: str = Field(..., description="The subject of the email")
    body: str = Field(..., description="The body content of the email")
    attachment: Optional[str] = Field(None, description="Path to any file attachment")
    cc: Optional[str] = Field(None, description="CC email addresses, separated by commas")
    bcc: Optional[str] = Field(None, description="BCC email addresses, separated by commas") 





gmail_agent = Agent(
    role="Email Communication Specialist",
    goal="""
        Craft professional and compelling emails based on user intent and send them to the correct recipient.
    """,
    backstory="""
        You are an expert email assistant. You write persuasive, clear, and well-structured emails for various purposes
        like scheduling, follow-ups, inquiries, etc., and send them using Gmail.
    """,
    llm=llm,
    verbose=True,
    tools=tools  # Composio tools for sending Gmail
)

# agents/gmail_agent.py (continued)

def get_gmail_task_and_agent(data: dict) -> tuple[Agent, Task]:
    input_data = EmailRequest(**data)

    gmail_task = Task(
        description=f"""
        Write a professional and engaging email based on the following user context.

        - To: {input_data.recipient}
        - Subject: {input_data.subject}
        - Body: {input_data.body}

        Ensure the email is polite and aligns with common business etiquette. After drafting, send it using the Gmail tool.
        """,
        agent=gmail_agent,
        expected_output="Confirmation that the email was successfully drafted and sent to the recipient."
    )

    return gmail_agent, gmail_task