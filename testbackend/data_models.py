from pydantic import BaseModel
from typing import List


from enum import Enum

class Intent(Enum):
    Find = 1
    Store = 2
    Other = 3

class Item(BaseModel):
    item: str
    location: str

    def __str__(self):
        return f"Item: {self.item}, Location: {self.location}"

class Items(BaseModel):
    items: List[Item]

    def __str__(self):
        return "\n".join(str(item) for item in self.items)