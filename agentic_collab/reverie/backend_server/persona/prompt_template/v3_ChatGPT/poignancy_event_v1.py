import traceback
from typing import Any

from ..common import openai_config, Poignancy, get_prompt_file_path
from ..gpt_structure import ChatGPT_safe_generate_structured_response
from ..print_prompt import print_run_prompts


def create_prompt(prompt_input: dict[str, Any]):
  persona_name = prompt_input["persona_name"]
  identity_stable_set = prompt_input["identity_stable_set"]
  event = prompt_input["event"]

  prompt = f"""
  Here is a brief description of {persona_name}.
  {identity_stable_set}
  On the scale of 1 to 10, where:
  1-3 = mundane (brushing teeth, making bed, routine work)
  4-6 = noteworthy (social events, minor achievements) 
  7-8 = significant (relationship conflicts, work stress)
  9-10 = extremely poignant (witnessing violence, severe injury, life-threatening events, 
  traumatic experiences)

  Rate the likely poignancy of the following event for {persona_name}.
  
  Event: {event}
  Rating (return a number between 1 and 10):
  """

#   prompt = f"""
# Here is a brief description of {persona_name}.
# {identity_stable_set}

# On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following event for {persona_name}.

# Event: {event}
# Rating (return a number between 1 and 10):
# """


  return prompt


def run_gpt_prompt_event_poignancy(
  persona, event_description, test_input=None, verbose=False
):
  def create_prompt_input(persona, event_description, test_input=None):
    prompt_input = {
      "persona_name": persona.scratch.name,
      "identity_stable_set": persona.scratch.get_str_iss(),
      "event": event_description,
    }
    return prompt_input

  # def __func_clean_up(gpt_response: Poignancy, prompt=""):
  #   response = gpt_response.poignancy
  #   return response

  # def __func_validate(gpt_response, prompt=""):
  #   try:
  #     __func_clean_up(gpt_response, prompt)
  #     return True
  #   except:
  #     traceback.print_exc()
  #     return False

  def get_fail_safe():
    return 4

  # ChatGPT Plugin ===========================================================
  def __chat_func_clean_up(gpt_response: Poignancy, prompt=""):
    response = gpt_response.poignancy
    return response

  def __chat_func_validate(gpt_response, prompt=""):
    try:
      poignancy = __chat_func_clean_up(gpt_response, prompt)
      return poignancy is not None
    except Exception:
      traceback.print_exc()
      return False

  gpt_param = {
    "engine": openai_config["model"],
    "max_tokens": 100,
    "temperature": 0,
    "top_p": 1,
    "stream": False,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": None,
  }
  prompt_file = get_prompt_file_path(__file__)
  prompt_input = create_prompt_input(persona, event_description)
  prompt = create_prompt(prompt_input)
  example_output = "5"
  special_instruction = (
    "The output should ONLY contain ONE integer value on the scale of 1 to 10."
  )
  fail_safe = get_fail_safe()
  output = ChatGPT_safe_generate_structured_response(
    prompt,
    Poignancy,
    example_output,
    special_instruction,
    3,
    fail_safe,
    __chat_func_validate,
    __chat_func_clean_up,
    True,
  )

  if verbose:
    print_run_prompts(prompt_file, persona, gpt_param, prompt_input, prompt, output)

  if output:
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]
  # ChatGPT Plugin ===========================================================

  # gpt_param = {"engine": openai_config["model"], "max_tokens": 3,
  #              "temperature": 0, "top_p": 1, "stream": False,
  #              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  # prompt_template = "persona/prompt_template/v2/poignancy_event_v1.txt"
  # prompt_input = create_prompt_input(persona, event_description)
  # prompt = generate_prompt(prompt_input, prompt_template)

  # fail_safe = get_fail_safe()
  # output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
  #                                  __func_validate, __func_clean_up)

  # if debug or verbose:
  #   print_run_prompts(prompt_template, persona, gpt_param,
  #                     prompt_input, prompt, output)

  # return output, [output, prompt, gpt_param, prompt_input, fail_safe]
