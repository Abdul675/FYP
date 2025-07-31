from langchain_openai import ChatOpenAI
from common.openai_config import get_openai_model  # Assuming this is where get_openai_model is defined

# Initialize the OpenAI model using the existing function
openai_model = ChatOpenAI(temperature=0.7, model=get_openai_model())

# Initialize BaseCache to avoid the error
#openai_model.cache = openai_model._cache_cls()

# Rebuild the model after initialization
openai_model.model_rebuild()

def fallback_response(user_input: str) -> str:
    prompt = f"""
    You are a helpful assistant. The user said: "{user_input}"

    If the user is trying to perform a task but hasn't provided complete input, guide them to clarify the missing details. For example:
    - If creating an event, ask for the event name, date, and attendees.
    - If uploading a file, ask for the file name and folder location.

    If the user asks general questions (e.g., "What can you do?" or "Tell me a joke"), respond with relevant answers:
    - "I can help with tasks like emails, scheduling events, file management, and more."

    If a task failed due to missing details or incorrect input, let the user know what is needed. For example:
    - "It looks like the event is missing a start date. Could you provide that?"

    Be sure to maintain a friendly and conversational tone.

    Response:
    """
    # Use the pre-configured OpenAI model to generate a response
    return openai_model.predict(prompt)
