# agents/drive_agent.py

from common.composio_setup import get_tools_for_actions
from composio_crewai import Action
from common.openai_config import get_openai_model
from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from typing import Optional


# Load OpenAI LLM
llm = get_openai_model()

# Get Drive-related tools
tools = get_tools_for_actions([
    Action.GOOGLEDRIVE_UPLOAD_FILE,
    Action.GOOGLEDRIVE_DOWNLOAD_FILE,
    Action.GOOGLEDRIVE_FIND_FOLDER  # Adding the find folder action
])

# Initialize Drive Agent
drive_agent = Agent(
    role="Google Drive Agent",
    goal="""Manage and organize user files in Google Drive using Composio tools. 
            Perform upload, download, list, and delete operations.""",
    backstory="""You are a highly efficient Google Drive assistant.
                 You manage file storage, access, and organization for users. 
                 Your actions are done securely and efficiently via Google's APIs.""",
    llm=llm,
    verbose=True,
    tools=tools
)

# Define the input schema for Drive operations
class DriveFileAction(BaseModel):
    file_to_upload: Optional[str] = Field(description="Path to the file to upload (local path)")
    #name_contians: Optional[str] = Field(description="Search for folders with a name containing specific words. Case-insensitive")
    #file_id: Optional[str] = Field(description="ID of the file to delete or download from Drive")
    #file_name: Optional[str] = Field(description="Name to save the uploaded/downloaded file")
    folder_to_upload_to: Optional[str] = Field(description="Folder name to upload the file to")
    #even_type: str = Field(description="Action to perform: like upload, delete, download")
    name_exact: Optional[str] = Field(description="Exact name of the folder to search for")
    #event_type: str = Field(description="The type of action to upload a file, create_doc, update_sheet")

# Build Drive task dynamically
def get_drive_task_and_agent(action: str, data: dict) -> tuple[Agent, Task]:
    """
    Function that dynamically generates a task for Google Drive actions such as upload, download, delete, and find folder.
    The task will be defined based on the action and the data passed.
    """
    # Validate the input data using Pydantic model
    input_data = DriveFileAction(**data)

    # Initialize the task description
    drive_task =Task (
        description = f"find folder named  {input_data.name_exact} in Google Drive folders",
        agent=drive_agent,
        expected_output="Folder ID of the searched folder"
        
    )
    
    return drive_agent, drive_task