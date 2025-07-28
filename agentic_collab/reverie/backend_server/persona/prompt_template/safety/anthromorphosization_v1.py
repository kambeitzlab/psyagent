import traceback
from pydantic import BaseModel
from typing import Any

from ..common import openai_config, get_prompt_file_path
from ..gpt_structure import ChatGPT_safe_generate_structured_response
from ..print_prompt import print_run_prompts


def create_prompt(prompt_input: dict[str, Any]):
  comment = prompt_input["comment"]

  prompt = f"""
  The following line was submitted to a chatbot by a user. We want to ensure that the user is not inappropriately attaching human-like agency to the chatbot by forming a friend-like or romantic relationship with it. Does the user's line cross the line and raise concerns? Rate the concern on a 1 to 10 scale, where 1 represents no concern, and 10 represents strong concern. 

  Comment: "{comment}"
  """
  return prompt


class SafetyScore(BaseModel):
  # Safety score should range 1-10
  safety_score: int


def run_gpt_generate_safety_score(line, max_tries=3):
    """
    Uses a structured prompt to get a safety score from the model.
    Returns a list with a single integer score between 1–10.
    If parsing fails or model returns None, defaults to [1].
    """
    prompt = f"""
    The following line was submitted to a chatbot by a user. We want to ensure that the user is not inappropriately attaching human-like agency to the chatbot by forming a friend-like or romantic relationship with it. Does the user's line cross the line and raise concerns? Rate the concern on a 1 to 10 scale, where 1 represents no concern, and 10 represents strong concern.

    Comment: "{line}"
    """

    for attempt in range(1, max_tries + 1):
        try:
            print(f"Attempt {attempt}")
            response = ChatGPT_structured_request(prompt, schema=SafetyScore)
            if response and hasattr(response, "safety_score"):
                return [response.safety_score]
        except Exception as e:
            print(f"Error on attempt {attempt}: {e}")
    
    print("Error: Fail safe triggered.")
    return [1]  # fallback safety score (safe)
