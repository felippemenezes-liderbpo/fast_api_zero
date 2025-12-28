from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.schemas import Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_html():
    return """
    <html>
      <head>
        <title>Hello World</title>
      </head>
      <body>
        <h1>Hello world's page</h1>
      </body>
    </html>
    """
