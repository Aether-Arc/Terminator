from pydantic import BaseModel
from typing import List


class EventInput(BaseModel):

    name: str
    venue: str
    days: int
    tracks: List[str]
    speakers: List[str]