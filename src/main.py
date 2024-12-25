from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from fastapi.responses import RedirectResponse

import multiprocessing as mp

from parsing import Parser

from schemas import ParsingSchema, ResultSchema, CardSchema

import uvicorn
app = FastAPI()

app.mount("/home", StaticFiles(directory="static", html=True), name="static")

router = APIRouter()

@router.post('/parsing')
async def parse(data: ParsingSchema) -> ResultSchema:
    data = data.model_dump()
    # count_of_process = data['count_of_process']

    parser = Parser(**data, headless=True)
    collect_data = parser.parse()

    return ResultSchema(cards=collect_data)

@router.get('/')
async def index():
    return RedirectResponse('/home/')

app.include_router(router)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
