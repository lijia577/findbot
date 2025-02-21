import faiss
from langchain_openai.embeddings import OpenAIEmbeddings
import numpy as np
from openai import OpenAI
# from dotenv import load_dotenv
# import json
from data_models import Item, Items, Intent
# from typing import Optional
import logging
from extract_gpt4 import extract_gpt4
from readwrite_db import *

# Configure logging
logging.basicConfig(level=logging.ERROR, filename='error.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# load_dotenv()
client = OpenAI()

embedding_model = OpenAIEmbeddings()


def get_intent(message: str, max_retries=3) -> Intent:
    prompt = (f"Help understand user intent, if the user is trying to find or location items, return 1, if the user is "
              f"describe items and their locations, return 2, otherwise, return 3. Just output the number, don't say "
              f"anything else."
              f"Message: '{message}'.")
    retries = 0
    while retries < max_retries:
        try:
            response = client.chat.completions.create(model="gpt-3.5-turbo",
                                                      messages=[{"role": "user", "content": prompt}])
            data = response.choices[0].message.content
            intent_value = int(data)

            # Map the integer to the corresponding Intent enum
            if intent_value == 1:
                return Intent.Find
            elif intent_value == 2:
                return Intent.Store
            elif intent_value == 3:
                return Intent.Other
            else:
                raise ValueError("Invalid intent value received.")

        except ValueError as e:
            logging.error("ValueError: Invalid input received. Details: %s", e)
            retries += 1
        except Exception as e:
            logging.error("Unexpected error: %s", e)
            retries += 1

    # If all retries are exhausted, raise an exception or return a default value
    logging.error("Max retries reached. Unable to obtain valid intent.")
    raise ValueError("Max retries reached. No valid intent input provided.")

def answer(message):
    intent = get_intent(message)
    if intent == Intent.Find:
        return process_find(message)
    elif intent == Intent.Store:
        return process_store(message)
    else:
        return process_store(message)


def process_find(message) -> str:
    return find_items_from_db(message)
    # return find_items_static_local(message)


def process_store(message):
    stored_items = extract_gpt4(message)
    store_item_details(stored_items)
    return str(stored_items)

def process_others(message):
    return "sorry I can't help with that"

# print(process_store("cat and dog are on the table"))


# Example items with locations
items = [
    {"name": "light bulbs", "location": "kitchen pantry, layer 2, bin 3"},
    {"name": "batteries", "location": "living room drawer"},
    {"name": "AA batteries", "location": "kitchen, second drawer"},
    {"name": "spare home keys", "location": "bedroom, night stand"},
    {"name": "tacoma car keys", "location": "living room, under the TV"},
    {"name": "BMW car keys", "location": "kitchen counter"},
    {"name": "Christmas Tree Top", "location": "attic"},
    {"name": "Christmas inflatable", "location": "attic"},
    {"name": "Christmas ornaments", "location": "attic"},
]



def create_vector(items):
    texts = [f"{item['name']}" for item in items]
    # Generate embeddings

    vectors = np.array(embedding_model.embed_documents(texts), dtype='float32')

    # Create FAISS index
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    item_map = {i: items[i] for i in range(len(items))}  # Map index to item
    return index, item_map


def find_items_static_local(query, items=items, top_k=5, threshold=0.4) -> str:  # Lower threshold = higher precision
    index, item_map = create_vector(items)
    query_vec = np.array(embedding_model.embed_query(query), dtype='float32').reshape(1, -1)
    D, I = index.search(query_vec, top_k)  # Retrieve top_k matches

    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx in item_map and dist < threshold:  # Filter weak matches
            item = item_map[idx]
            results.append(f"'{item['name']}' is in {item['location']} (score: {dist:.4f})")

    return "\n".join(results) if results else "Item not found."

def find_items_from_db(query, top_k=5, threshold=0.4):  # Lower threshold = higher precision
    items = retrieve_items()
    vectors = np.array(embedding_model.embed_documents(items), dtype='float32')
    # Create FAISS index
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    item_map = {i: items[i] for i in range(len(items))}
    query_vec = np.array(embedding_model.embed_query(query), dtype='float32').reshape(1, -1)
    D, I = index.search(query_vec, top_k)  # Retrieve top_k matches

    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx in item_map and dist < threshold:  # Filter weak matches
            item_name = item_map[idx]
            print(item_name)
            result = retrieve_location_by_item(item_name)
            results.append(f"'{result} (score: {dist:.4f})")

    return " | ".join(results) if results else "Item not found."

# print(find_items_from_db("car keys?"))
