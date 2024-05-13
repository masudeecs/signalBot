from fastapi import APIRouter, Depends, status

from schemas.gpt_schemas import ChatPromptsSchema
from config.security import get_current_user, oauth2_scheme
from services.eee_gpt import question_and_answer
from responses.user import GPTResponse

gpt_router = APIRouter(
    prefix="/conversation",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme), Depends(get_current_user)]
)

@gpt_router.post('', status_code=status.HTTP_200_OK)
async def qna(data: ChatPromptsSchema, user = Depends(get_current_user)):
    txt_response = await question_and_answer(data.question, user.name)
    return {"txt_response": txt_response}
