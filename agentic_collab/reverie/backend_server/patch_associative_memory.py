# File: patch_associative_memory.py
import os
import sys
import json
import traceback

# Add the path to the directory containing reverie.py
os.chdir('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')
sys.path.append('/Users/josephkambeitz/Desktop/Research/simulacra/agentic_collab/reverie/backend_server')

# Import the original class
from persona.memory_structures.associative_memory import AssociativeMemory
from persona.memory_structures.associative_memory import ConceptNode

# Save the original __init__ method
original_init = AssociativeMemory.__init__

def patched_init(self, f_saved):
    """Patched version of AssociativeMemory.__init__ that handles missing keys"""
    # Start with empty structures
    self.seq_event = []
    self.seq_chat = []
    self.seq_thought = []
    self.nodes = dict()
    self.id_to_node = dict()
    self.embeddings = dict()
    
    # Add a default embedding for None key
    self.embeddings[None] = [0.0] * 1536  # Default zero embedding vector
    
    # Skip if directory doesn't exist
    if not os.path.exists(f_saved):
        print(f"WARNING: Directory {f_saved} does not exist, initializing empty memory")
        return
    
    try:
        # Load embeddings
        if os.path.exists(f"{f_saved}/embeddings.json"):
            print("Loading embeddings file...")
            with open(f"{f_saved}/embeddings.json") as json_file:
                self.embeddings.update(json.load(json_file))
                print(f"Loaded {len(self.embeddings)} embeddings")
        else:
            print(f"WARNING: No embeddings file found at {f_saved}/embeddings.json")
            
        # Load nodes
        if os.path.exists(f"{f_saved}/nodes.json"):
            print("Loading nodes file...")
            with open(f"{f_saved}/nodes.json") as json_file:
                self.nodes = json.load(json_file)
                print(f"Loaded {len(self.nodes)} nodes")
                
            # Print some sample node keys to debug
            if len(self.nodes) > 0:
                sample_node_id = next(iter(self.nodes))
                sample_node = self.nodes[sample_node_id]
                print(f"Sample node keys: {list(sample_node.keys())}")
                
            # Process nodes
            for node_id, node_details in self.nodes.items():
                try:
                    # Get node details with fallbacks for missing fields
                    node_type = node_details.get("node_type", "event")  # Default to event
                    created = node_details.get("created", "")
                    expiration = node_details.get("expiration", "")
                    subject = node_details.get("subject", "")
                    predicate = node_details.get("predicate", "")
                    object = node_details.get("object", "")
                    description = node_details.get("description", "")
                    
                    # Handle missing embedding key
                    embedding_key = node_details.get("embedding_key")
                    if embedding_key is None:
                        print(f"Node {node_id} has None embedding_key, using fallback")
                        node_details["embedding_key"] = f"fixed_key_{node_id}"
                        embedding_key = node_details["embedding_key"]
                        
                        # Also add a default embedding for this key
                        if embedding_key not in self.embeddings:
                            self.embeddings[embedding_key] = [0.0] * 1536
                    
                    # Get the embedding pair
                    embedding_pair = (embedding_key, self.embeddings.get(embedding_key, self.embeddings[None]))
                    
                    poignancy = node_details.get("poignancy", 5)  # Default poignancy
                    filling = node_details.get("filling", [])
                    keywords = node_details.get("keywords", [])
                    last_accessed = node_details.get("last_accessed", created)
                    
                    # Create the node
                    node = ConceptNode(node_id=node_id, 
                                    node_type=node_type,
                                    created=created,
                                    expiration=expiration,
                                    subject=subject,
                                    predicate=predicate,
                                    object=object,
                                    description=description,
                                    embedding_key=embedding_key,
                                    embedding_pair=embedding_pair,
                                    poignancy=poignancy,
                                    filling=filling,
                                    keywords=keywords,
                                    last_accessed=last_accessed)
                    
                    # Add node to appropriate sequence
                    if node_type == "event":
                        self.seq_event.append(node)
                    elif node_type == "chat":
                        self.seq_chat.append(node)
                    elif node_type == "thought":
                        self.seq_thought.append(node)
                    
                    # Add to id_to_node mapping
                    self.id_to_node[node_id] = node
                    
                except Exception as e:
                    print(f"ERROR processing node {node_id}: {e}")
                    continue
                    
        else:
            print(f"WARNING: No nodes file found at {f_saved}/nodes.json")
        
        print("AssociativeMemory patched initialization complete!")
        print(f"Loaded {len(self.seq_event)} events, {len(self.seq_chat)} chats, {len(self.seq_thought)} thoughts")
        
    except Exception as e:
        print(f"ERROR in patched AssociativeMemory.__init__: {e}")
        traceback.print_exc()
        # Initialize with empty state instead of raising error
        self.seq_event = []
        self.seq_chat = []
        self.seq_thought = []

# Apply the patch
AssociativeMemory.__init__ = patched_init

print("AssociativeMemory class patched to handle missing keys!")