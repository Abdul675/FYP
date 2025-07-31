from common.composio_setup import get_tools_for_actions
from composio_crewai import Action

# getting required tools from composio for this agent 

tools = get_tools_for_actions([
    Action.GOOGLESHEETS_LOOKUP_SPREADSHEET_ROW,
    Action.GOOGLECALENDAR_FIND_FREE_SLOTS,
    Action.GOOGLECALENDAR_CREATE_EVENT,
    Action.GMAIL_CREATE_EMAIL_DRAFT
])

