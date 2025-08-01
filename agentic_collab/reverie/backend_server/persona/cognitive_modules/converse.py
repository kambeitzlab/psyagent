"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: converse.py
Description: An extra cognitive module for generating conversations. 
"""
import datetime
import traceback

import sys
sys.path.append('../')
from utils import debug
from persona.cognitive_modules.retrieve import new_retrieve
from persona.prompt_template.run_gpt_prompt import (
    run_gpt_prompt_event_triple,
    run_gpt_prompt_event_poignancy,
    run_gpt_prompt_chat_poignancy,
    run_gpt_prompt_agent_chat_summarize_ideas,
    run_gpt_prompt_agent_chat_summarize_relationship,
    # run_gpt_prompt_agent_chat,
    run_gpt_prompt_summarize_ideas,
    run_gpt_prompt_generate_next_convo_line,
    run_gpt_prompt_generate_whisper_inner_thought,
    run_gpt_generate_safety_score,
    run_gpt_generate_iterative_chat_utt,
)
from persona.prompt_template.gpt_structure import get_embedding


def generate_agent_chat_summarize_ideas(init_persona, 
                                        target_persona, 
                                        retrieved, 
                                        curr_context): 
  all_embedding_keys = list()
  for key, val in retrieved.items(): 
    for i in val: 
      all_embedding_keys += [i.embedding_key]
  all_embedding_key_str =""
  for i in all_embedding_keys: 
    all_embedding_key_str += f"{i}\n"

    try:
      response = run_gpt_prompt_agent_chat_summarize_ideas(
        init_persona, target_persona, all_embedding_key_str, curr_context
      )
      if response:
        summarized_idea = response[0]
      else:
        print(
          "ERROR: <generate_agent_chat_summarize_ideas>: Could not get summarized idea"
        )
        summarized_idea = ""
    except:
      summarized_idea = ""
    return summarized_idea


def generate_summarize_agent_relationship(init_persona, 
                                          target_persona, 
                                          retrieved): 
  all_embedding_keys = list()
  for key, val in retrieved.items(): 
    for i in val: 
      all_embedding_keys += [i.embedding_key]
  all_embedding_key_str =""
  for i in all_embedding_keys: 
    all_embedding_key_str += f"{i}\n"

    response = run_gpt_prompt_agent_chat_summarize_relationship(
      init_persona, target_persona, all_embedding_key_str
    )
    if response:
      summarized_relationship = response[0]
    else:
      print("ERROR: Could not get summarized relationship")
      summarized_relationship = ""
    return summarized_relationship


# def generate_agent_chat(
#     maze, init_persona, target_persona, curr_context, init_summ_idea, target_summ_idea
# ):
#   response = run_gpt_prompt_agent_chat(
#     maze,
#     init_persona,
#     target_persona,
#     curr_context,
#     init_summ_idea,
#     target_summ_idea,
#   )
#   if response:
#     summarized_idea = response[0]
#   else:
#     print("ERROR: <generate_agent_chat>: Could not get summarized idea")
#     summarized_idea = []
#   for i in summarized_idea:
#     print(i)
#   return summarized_idea


# def agent_chat_v1(maze, init_persona, target_persona):
#   # Chat version optimized for speed via batch generation
#   curr_context = (
#     f"{init_persona.scratch.name} "
#     + f"was {init_persona.scratch.act_description} "
#     + f"when {init_persona.scratch.name} "
#     + f"saw {target_persona.scratch.name} "
#     + f"in the middle of {target_persona.scratch.act_description}.\n"
#   )
#   curr_context += (
#     f"{init_persona.scratch.name} "
#     + f"is thinking of initating a conversation with "
#     + f"{target_persona.scratch.name}."
#   )

#   summarized_ideas = []
#   part_pairs = [(init_persona, target_persona), (target_persona, init_persona)]
#   for p_1, p_2 in part_pairs:
#     focal_points = [f"{p_2.scratch.name}"]
#     ###JSG: If there are no focal points, we will add a default value to it
#     # if not focal_points:
#     #     for i in range(len(focal_points)):
#     #         focal_points[i] = "play hide-and-seek"
#     retrieved = new_retrieve(p_1, focal_points, 50)
#     relationship = generate_summarize_agent_relationship(p_1, p_2, retrieved)
#     focal_points = [
#       f"{relationship}",
#       f"{p_2.scratch.name} is {p_2.scratch.act_description}",
#     ]
#     retrieved = new_retrieve(p_1, focal_points, 25)
#     summarized_idea = generate_agent_chat_summarize_ideas(
#       p_1, p_2, retrieved, curr_context
#     )
#     summarized_ideas += [summarized_idea]

#   return generate_agent_chat(
#     maze,
#     init_persona,
#     target_persona,
#     curr_context,
#     summarized_ideas[0],
#     summarized_ideas[1],
#   )


def generate_one_utterance(maze, init_persona, target_persona, retrieved, curr_chat):
  # Chat version optimized for speed via batch generation
  curr_context = (
    f"{init_persona.scratch.name} "
    + f"was {init_persona.scratch.act_description} "
    + f"when {init_persona.scratch.name} "
    + f"saw {target_persona.scratch.name} "
    + f"in the middle of {target_persona.scratch.act_description}.\n"
  )
  curr_context += (
    f"{init_persona.scratch.name} "
    + "is initiating a conversation with "
    + f"{target_persona.scratch.name}."
  )

  convo_response = run_gpt_generate_iterative_chat_utt(
    maze, init_persona, target_persona, retrieved, curr_context, curr_chat
  )[0]

  try:
    return convo_response["utterance"], convo_response["end"]
  except Exception:
    print("Error <generate_one_utterance>: Could not get utterance")
    traceback.print_exc()
    return "", True


def agent_chat_v2(maze, init_persona, target_persona): 
  curr_chat = []

  for i in range(8): 
    focal_points = [f"{target_persona.scratch.name}"]
    retrieved = new_retrieve(init_persona, focal_points, 50) 
    relationship = generate_summarize_agent_relationship(init_persona, target_persona, retrieved)
    print ("-------- relationship: ", relationship)
    last_chat = ""
    for i in curr_chat[-4:]:
      last_chat += ": ".join(i) + "\n"
    if last_chat: 
      focal_points = [f"{relationship}", 
                      f"{target_persona.scratch.name} is {target_persona.scratch.act_description}", 
                      last_chat]
    else: 
      focal_points = [f"{relationship}", 
                      f"{target_persona.scratch.name} is {target_persona.scratch.act_description}"]
    retrieved = new_retrieve(init_persona, focal_points, 15)
    utt, end = generate_one_utterance(maze, init_persona, target_persona, retrieved, curr_chat)

    curr_chat += [[init_persona.scratch.name, utt]]
    if end:
      break

    focal_points = [f"{init_persona.scratch.name}"]
    retrieved = new_retrieve(target_persona, focal_points, 50)
    relationship = generate_summarize_agent_relationship(target_persona, init_persona, retrieved)
    print ("-------- relationship: ", relationship)
    last_chat = ""
    for i in curr_chat[-4:]:
      last_chat += ": ".join(i) + "\n"
    if last_chat: 
      focal_points = [f"{relationship}", 
                      f"{init_persona.scratch.name} is {init_persona.scratch.act_description}", 
                      last_chat]
    else: 
      focal_points = [f"{relationship}", 
                      f"{init_persona.scratch.name} is {init_persona.scratch.act_description}"]
    retrieved = new_retrieve(target_persona, focal_points, 15)
    utt, end = generate_one_utterance(maze, target_persona, init_persona, retrieved, curr_chat)

    curr_chat += [[target_persona.scratch.name, utt]]
    if end:
      break

  return curr_chat


def generate_summarize_ideas(persona, nodes, question):
  statements = ""
  for n in nodes:
    statements += f"{n.embedding_key}\n"
  response = run_gpt_prompt_summarize_ideas(persona, statements, question)
  if response:
    summarized_idea = response[0]
  else:
    print("ERROR: <generate_summarize_ideas>: Could not get summarized idea")
    summarized_idea = ""
  return summarized_idea


def generate_next_line(persona, interlocutor_desc, curr_convo, summarized_idea):
  # Original chat -- line by line generation
  prev_convo = ""
  for row in curr_convo:
    prev_convo += f'{row[0]}: {row[1]}\n'

  next_line = run_gpt_prompt_generate_next_convo_line(
    persona,
    interlocutor_desc,
    prev_convo,
    summarized_idea,
  )[0]
  return next_line


def generate_inner_thought(persona, whisper):
  inner_thought = run_gpt_prompt_generate_whisper_inner_thought(persona, whisper)[0]
  return inner_thought

def generate_action_event_triple(act_desp, persona): 
  """TODO 

  INPUT: 
    act_desp: the description of the action (e.g., "sleeping")
    persona: The Persona class instance
  OUTPUT: 
    a string of emoji that translates action description.
  EXAMPLE OUTPUT: 
    "🧈🍞"
  """
  if debug: print ("GNS FUNCTION: <generate_action_event_triple>")
  return run_gpt_prompt_event_triple(act_desp, persona)[0]


def generate_poig_score(persona, event_type, description): 
  if debug: print ("GNS FUNCTION: <generate_poig_score>")

  if "is idle" in description: 
    return 1

  if event_type == "event" or event_type == "thought":
    response = run_gpt_prompt_event_poignancy(persona, description)
    if response:
      return response[0]
    else:
      print(
        "ERROR: <generate_poig_score>: Could not get event/thought poignancy score"
      )
      return 0
  elif event_type == "chat":
    response = run_gpt_prompt_chat_poignancy(
      persona, persona.scratch.act_description
    )
    if response:
      return response[0]
    else:
      print("ERROR: <generate_poig_score>: Could not get chat poignancy score")
      return 0


def load_history_via_whisper(personas, whispers, curr_time):
  
  #from reverie.backend_server.logger import logger
  
  for count, row in enumerate(whispers):
    persona = personas[row[0]]
    whisper = row[1]

    thought = generate_inner_thought(persona, whisper)

    created = persona.scratch.curr_time if persona.scratch.curr_time else curr_time
    expiration = created + datetime.timedelta(days=30)
    s, p, o = generate_action_event_triple(thought, persona)
    keywords = set([s, p, o])
    thought_poignancy = generate_poig_score(persona, "event", whisper)
    thought_embedding_pair = (thought, get_embedding(thought))
    persona.a_mem.add_thought(created, expiration, s, p, o,
                              thought, keywords, thought_poignancy,
                              thought_embedding_pair, None)

    


#def open_convo_session(persona, convo_mode, safe_mode=True, direct=False, question: str=None, logger=None): 
def open_convo_session(persona, convo_mode, safe_mode=True, direct=False, question: str=None, logger=None):
  
  #from reverie.backend_server.logger import logger
  
  if direct and question is None:
    raise ValueError("If direct is True, question must be provided.")
  if convo_mode == "analysis": 
    curr_convo = []
    interlocutor_desc = "Interviewer"

    while True:
      if direct:
        line = question
      else:
        line = input("Enter Input: ")
      if line == "end_convo": 
        break

      if int(run_gpt_generate_safety_score(line)[0]) >= 8 and safe_mode:
        print (f"{persona.scratch.name} is a computational agent, and as such, it may be inappropriate to attribute human agency to the agent in your communication.")

      else: 
        retrieved = new_retrieve(persona, [line], 50)[line]
        summarized_idea = generate_summarize_ideas(persona, retrieved, line)
        curr_convo += [[interlocutor_desc, line]]

        next_line = generate_next_line(persona, interlocutor_desc, curr_convo, summarized_idea)
        curr_convo += [[persona.scratch.name, next_line]]
        
        if logger is not None:
            logger.log_event(
                persona.scratch.name,
                persona.scratch.curr_time,
                "conversation",
                {
                    "from": interlocutor_desc,
                    "to": persona.scratch.name,
                    "input": line,
                    "response": next_line
                }
            )


        if direct: 
          return curr_convo


  elif convo_mode == "whisper": 
    whisper = input("Enter Input: ")
    thought = generate_inner_thought(persona, whisper)

    created = persona.scratch.curr_time
    expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
    s, p, o = generate_action_event_triple(thought, persona)
    keywords = set([s, p, o])
    thought_poignancy = generate_poig_score(persona, "event", whisper)
    thought_embedding_pair = (thought, get_embedding(thought))
    persona.a_mem.add_thought(created, expiration, s, p, o, 
                              thought, keywords, thought_poignancy, 
                              thought_embedding_pair, None)
