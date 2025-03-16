from typing import List, Literal
from pydantic import BaseModel


class DirectoryInfo(BaseModel):
    name: str
    path: str
