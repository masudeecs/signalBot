# from pydantic import BaseModel
from pydantic import BaseModel

class ChatPromptsSchema(BaseModel):
    question: str
    # histoty: list[str] | None = None