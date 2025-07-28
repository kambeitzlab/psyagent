"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: print_prompt.py
Description: For printing prompts when the setting for verbose is set to True.
"""

##############################################################################
#                    PERSONA Chapter 1: Prompt Structures                    #
##############################################################################


def print_run_prompts(
    prompt_file="",
    persona=None,
    gpt_param=None,
    prompt_input=None,
    prompt="",
    output=None,
):
    # commented this out to avoid overflow in console which clouds my debug messages
#     print(f'''

# === File: {prompt_file}
# ~~~ persona    ---------------------------------------------------
# {persona.name if persona else "None"}

# ~~~ gpt_param ----------------------------------------------------
# {gpt_param}

# ~~~ prompt_input    ----------------------------------------------
# {prompt_input}

# ~~~ final prompt    ----------------------------------------------------
# {prompt}

# ~~~ processed output    ----------------------------------------------------
# {output}

# === END ==========================================================

# ''', flush=True)

    print('')
