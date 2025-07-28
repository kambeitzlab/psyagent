"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: associative_memory.py
Description: Defines the core long-term memory module for generative agents.

Note (May 1, 2023) -- this class is the Memory Stream module in the generative
agents paper. 
"""
import json
import datetime
import os

class ConceptNode: 
  def __init__(self,
               node_id, node_count, type_count, node_type, depth,
               created, expiration, 
               s, p, o, 
               description, embedding_key, poignancy, keywords, filling): 
    self.node_id = node_id
    self.node_count = node_count
    self.type_count = type_count
    self.type = node_type # thought / event / chat
    self.depth = depth

    self.created = created
    self.expiration = expiration
    self.last_accessed = self.created

    self.subject = s
    self.predicate = p
    self.object = o

    self.description = description
    self.embedding_key = embedding_key
    self.poignancy = poignancy
    self.keywords = keywords
    self.filling = filling


  def spo_summary(self): 
    return (self.subject, self.predicate, self.object)


class AssociativeMemory: 
    
  def __init__(self, f_saved): 
    """
    Initialize AssociativeMemory with data from saved file, with robust handling
    of missing or inconsistent fields.
    """
    # Initialize empty structures
    self.id_to_node = dict()
    self.seq_event = []
    self.seq_thought = []
    self.seq_chat = []
    self.kw_to_event = dict()
    self.kw_to_thought = dict()
    self.kw_to_chat = dict()
    self.kw_strength_event = dict()
    self.kw_strength_thought = dict()
    self.embeddings = dict()
    
    # Default embedding for None keys
    self.embeddings[None] = [0.0] * 1536
    
    # Skip if directory doesn't exist
    if not os.path.exists(f_saved):
        print(f"WARNING: Directory {f_saved} does not exist, initializing empty memory")
        return
    
    try:
        # Load embeddings
        embeddings_file = f"{f_saved}/embeddings.json"
        if os.path.exists(embeddings_file):
            with open(embeddings_file) as json_file:
                self.embeddings.update(json.load(json_file))
            
            # If there's a null_key in embeddings, map it to None
            if "null_key" in self.embeddings:
                self.embeddings[None] = self.embeddings["null_key"]
                del self.embeddings["null_key"]
        else:
            print(f"WARNING: No embeddings file found at {embeddings_file}")
        
        # Load nodes
        nodes_file = f"{f_saved}/nodes.json"
        if os.path.exists(nodes_file):
            with open(nodes_file) as json_file:
                nodes_load = json.load(json_file)
            
            for count in range(len(nodes_load.keys())): 
                try:
                    node_id = f"node_{str(count+1)}"
                    if node_id not in nodes_load:
                        continue
                    
                    node_details = nodes_load[node_id]
                    
                    # Get fields with fallbacks for missing data
                    node_count = node_details.get("node_count", count+1)
                    type_count = node_details.get("type_count", 1)
                    node_type = node_details.get("type", node_details.get("node_type", "event"))
                    depth = node_details.get("depth", 0)
                    
                    # Handle created timestamp
                    created = node_details.get("created", "")
                    if created and not isinstance(created, datetime.datetime):
                        try:
                            created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
                        except:
                            created = datetime.datetime.now()
                    
                    # Handle expiration
                    expiration = None
                    if node_details.get("expiration"):
                        try:
                            expiration = datetime.datetime.strptime(node_details["expiration"], '%Y-%m-%d %H:%M:%S')
                        except:
                            expiration = None
                    
                    # Get SPO elements
                    s = node_details.get("subject", "")
                    p = node_details.get("predicate", "")
                    o = node_details.get("object", "")
                    
                    # Get other fields
                    description = node_details.get("description", "")
                    
                    # Handle missing or null embedding key
                    embedding_key = node_details.get("embedding_key")
                    if embedding_key is None or embedding_key == "null":
                        embedding_key = f"fixed_key_{node_id}"
                        
                        # Add a default embedding for this key
                        if embedding_key not in self.embeddings:
                            self.embeddings[embedding_key] = [0.0] * 1536
                    
                    embedding_pair = (embedding_key, self.embeddings.get(embedding_key, self.embeddings[None]))
                    poignancy = node_details.get("poignancy", 5)
                    keywords = set(node_details.get("keywords", []))
                    filling = node_details.get("filling", [])
                    
                    # Add node based on its type
                    if node_type == "event": 
                        self.add_event(created, expiration, s, p, o, 
                                description, keywords, poignancy, embedding_pair, filling)
                    elif node_type == "chat": 
                        self.add_chat(created, expiration, s, p, o, 
                                description, keywords, poignancy, embedding_pair, filling)
                    elif node_type == "thought": 
                        self.add_thought(created, expiration, s, p, o, 
                                description, keywords, poignancy, embedding_pair, filling)
                except Exception as e:
                    print(f"WARNING: Error processing node {node_id}: {e}")
                    continue
        else:
            print(f"WARNING: No nodes file found at {nodes_file}")
        
        # Load keyword strength data
        kw_strength_file = f"{f_saved}/kw_strength.json"
        if os.path.exists(kw_strength_file):
            try:
                kw_strength_load = json.load(open(kw_strength_file))
                if kw_strength_load.get("kw_strength_event"): 
                    self.kw_strength_event = kw_strength_load["kw_strength_event"]
                if kw_strength_load.get("kw_strength_thought"): 
                    self.kw_strength_thought = kw_strength_load["kw_strength_thought"]
            except Exception as e:
                print(f"WARNING: Error loading keyword strength data: {e}")
    
    except Exception as e:
        print(f"WARNING: Error in AssociativeMemory.__init__: {e}")
        import traceback
        traceback.print_exc()
        # Continue with empty memories rather than failing  
  
  def save(self, f_saved):
    """
    Save associative memory to a file.
    
    INPUT: 
      f_saved: Directory path where we will save our associative memory.
    OUTPUT: 
      None
    """
    # Create directory if it doesn't exist
    os.makedirs(f_saved, exist_ok=True)
    
    # Save the embeddings
    embeddings_dict = self.embeddings.copy()
    # Fix any None keys in embeddings
    if None in embeddings_dict:
        embeddings_dict["null_key"] = embeddings_dict[None]
        del embeddings_dict[None]
    
    with open(f"{f_saved}/embeddings.json", "w") as outfile:
      json.dump(embeddings_dict, outfile, indent=2) 
    
    # Save keyword strength data
    kw_strength = {
        "kw_strength_event": self.kw_strength_event,
        "kw_strength_thought": self.kw_strength_thought
    }
    with open(f"{f_saved}/kw_strength.json", "w") as outfile:
        json.dump(kw_strength, outfile, indent=2)
    
    # Save the nodes
    nodes_dict = {}
    for node_id, node in self.id_to_node.items():
        # Fix any None embedding keys
        embedding_key = node.embedding_key
        if embedding_key is None:
            embedding_key = f"fixed_key_{node_id}"
        
        # Get the node type from the object's type attribute
        node_type = getattr(node, "type", "event")
        
        # Convert datetime objects to strings
        created_str = ""
        if hasattr(node, "created"):
            if isinstance(node.created, datetime.datetime):
                created_str = node.created.strftime('%Y-%m-%d %H:%M:%S')
            else:
                created_str = str(node.created)
        
        expiration_str = ""
        if hasattr(node, "expiration") and node.expiration:
            if isinstance(node.expiration, datetime.datetime):
                expiration_str = node.expiration.strftime('%Y-%m-%d %H:%M:%S')
            else:
                expiration_str = str(node.expiration)
        
        last_accessed_str = ""
        if hasattr(node, "last_accessed"):
            if isinstance(node.last_accessed, datetime.datetime):
                last_accessed_str = node.last_accessed.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_accessed_str = str(node.last_accessed)
        elif hasattr(node, "created"):
            if isinstance(node.created, datetime.datetime):
                last_accessed_str = node.created.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_accessed_str = str(node.created)
        
        nodes_dict[node_id] = {
            # Include all required fields
            "node_count": getattr(node, "node_count", 1),
            "type_count": getattr(node, "type_count", 1),
            "type": node_type,
            "node_type": node_type,  # Include both for compatibility
            "depth": getattr(node, "depth", 0),
            "created": created_str,
            "expiration": expiration_str,
            "subject": getattr(node, "subject", ""),
            "predicate": getattr(node, "predicate", ""),
            "object": getattr(node, "object", ""),
            "description": getattr(node, "description", ""),
            "embedding_key": embedding_key,
            "poignancy": getattr(node, "poignancy", 5),
            "filling": getattr(node, "filling", []),
            "keywords": list(getattr(node, "keywords", set())),
            "last_accessed": last_accessed_str
        }
    
    with open(f"{f_saved}/nodes.json", "w") as outfile:
      json.dump(nodes_dict, outfile, indent=2)

  def add_event(self, created, expiration, s, p, o, 
                      description, keywords, poignancy, 
                      embedding_pair, filling):
    # Setting up the node ID and counts.
    node_count = len(self.id_to_node.keys()) + 1
    type_count = len(self.seq_event) + 1
    node_type = "event"
    node_id = f"node_{str(node_count)}"
    depth = 0

    # Node type specific clean up. 
    if "(" in description: 
      description = (" ".join(description.split()[:3]) 
                     + " " 
                     +  description.split("(")[-1][:-1])

    # Creating the <ConceptNode> object.
    node = ConceptNode(node_id, node_count, type_count, node_type, depth,
                       created, expiration, 
                       s, p, o, 
                       description, embedding_pair[0], 
                       poignancy, keywords, filling)

    # Creating various dictionary cache for fast access. 
    self.seq_event[0:0] = [node]
    keywords = [i.lower() for i in keywords]
    for kw in keywords: 
      if kw in self.kw_to_event: 
        self.kw_to_event[kw][0:0] = [node]
      else: 
        self.kw_to_event[kw] = [node]
    self.id_to_node[node_id] = node 

    # Adding in the kw_strength
    if f"{p} {o}" != "is idle":  
      for kw in keywords: 
        if kw in self.kw_strength_event: 
          self.kw_strength_event[kw] += 1
        else: 
          self.kw_strength_event[kw] = 1

    self.embeddings[embedding_pair[0]] = embedding_pair[1]

    return node


  def add_thought(self, created, expiration, s, p, o, 
                        description, keywords, poignancy, 
                        embedding_pair, filling):
    # Setting up the node ID and counts.
    node_count = len(self.id_to_node.keys()) + 1
    type_count = len(self.seq_thought) + 1
    node_type = "thought"
    node_id = f"node_{str(node_count)}"
    depth = 1 
    try: 
      if filling: 
        depth += max([self.id_to_node[i].depth for i in filling])
    except: 
      pass

    # Creating the <ConceptNode> object.
    node = ConceptNode(node_id, node_count, type_count, node_type, depth,
                       created, expiration, 
                       s, p, o, 
                       description, embedding_pair[0], poignancy, keywords, filling)

    # Creating various dictionary cache for fast access. 
    self.seq_thought[0:0] = [node]
    keywords = [i.lower() for i in keywords]
    for kw in keywords: 
      if kw in self.kw_to_thought: 
        self.kw_to_thought[kw][0:0] = [node]
      else: 
        self.kw_to_thought[kw] = [node]
    self.id_to_node[node_id] = node 

    # Adding in the kw_strength
    if f"{p} {o}" != "is idle":  
      for kw in keywords: 
        if kw in self.kw_strength_thought: 
          self.kw_strength_thought[kw] += 1
        else: 
          self.kw_strength_thought[kw] = 1

    self.embeddings[embedding_pair[0]] = embedding_pair[1]

    return node


  def add_chat(self, created, expiration, s, p, o, 
                     description, keywords, poignancy, 
                     embedding_pair, filling): 
    # Setting up the node ID and counts.
    node_count = len(self.id_to_node.keys()) + 1
    type_count = len(self.seq_chat) + 1
    node_type = "chat"
    node_id = f"node_{str(node_count)}"
    depth = 0

    # Creating the <ConceptNode> object.
    node = ConceptNode(node_id, node_count, type_count, node_type, depth,
                       created, expiration, 
                       s, p, o, 
                       description, embedding_pair[0], poignancy, keywords, filling)

    # Creating various dictionary cache for fast access. 
    self.seq_chat[0:0] = [node]
    keywords = [i.lower() for i in keywords]
    for kw in keywords: 
      if kw in self.kw_to_chat: 
        self.kw_to_chat[kw][0:0] = [node]
      else: 
        self.kw_to_chat[kw] = [node]
    self.id_to_node[node_id] = node 

    self.embeddings[embedding_pair[0]] = embedding_pair[1]
        
    return node


  def get_summarized_latest_events(self, retention): 
    ret_set = set()
    for e_node in self.seq_event[:retention]: 
      ret_set.add(e_node.spo_summary())
    return ret_set


  def get_str_seq_events(self): 
    ret_str = ""
    for count, event in enumerate(self.seq_event): 
      ret_str += f'{"Event", len(self.seq_event) - count, ": ", event.spo_summary(), " -- ", event.description}\n'
    return ret_str


  def get_str_seq_thoughts(self): 
    ret_str = ""
    for count, event in enumerate(self.seq_thought): 
      ret_str += f'{"Thought", len(self.seq_thought) - count, ": ", event.spo_summary(), " -- ", event.description}'
    return ret_str


  def get_str_seq_chats(self): 
    ret_str = ""
    for count, event in enumerate(self.seq_chat): 
      ret_str += f"with {event.object.content} ({event.description})\n"
      ret_str += f'{event.created.strftime("%B %d, %Y, %H:%M:%S")}\n'
      for row in event.filling: 
        ret_str += f"{row[0]}: {row[1]}\n"
    return ret_str


  def retrieve_relevant_thoughts(self, s_content, p_content, o_content): 
    contents = [s_content, p_content, o_content]

    ret = []
    for i in contents: 
      if i in self.kw_to_thought: 
        ret += self.kw_to_thought[i.lower()]

    ret = set(ret)
    return ret

  def retrieve_relevant_events(self, s_content, p_content, o_content):
    contents = [s_content, p_content, o_content]

    ret = []
    for i in contents:
      if i in self.kw_to_event:
        ret += self.kw_to_event[i]

    ret = set(ret)
    return ret

  def get_last_chat(self, target_persona_name):
    if target_persona_name.lower() in self.kw_to_chat:
      return self.kw_to_chat[target_persona_name.lower()][0]
    else: 
      return False

  def reduce_poignancy(self, poignancy, timestamp, decay_rate):
    current_time = datetime.datetime.now()
    time_diff = (current_time - timestamp).total_seconds()
    return poignancy * ((1 - decay_rate) ** time_diff)
