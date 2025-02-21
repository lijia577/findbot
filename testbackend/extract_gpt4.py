from openai import OpenAI
from dotenv import load_dotenv
from data_models import Items

# This version of retrieval uses GPT4 JSON schema. It's cool since it always sticks to the schema, less hallucination.

load_dotenv()
client = OpenAI()

def extract_gpt4(t) -> Items:
    p = "You are an expert at structured data extraction, load each item and location info from the input text."
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": p},
            {"role": "user", "content":  t}
        ],
        response_format=Items,
    )
    return completion.choices[0].message.parsed


if __name__ == "__main__":
    t = "I put a pair of leather gloves with fur inside the bedroom drawer, keys are on the living room desk, needles are on the bedroom desk white drawer, I think that's it."
    t = "In the kitchen cabinet A shelf 1 there is baking powder baking soda various seasonings various grains such as red beans"
    r = extract_gpt4(t)
    print(r)