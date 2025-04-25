from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.openapi.models import Response
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic
from fastapi.templating import Jinja2Templates
import secrets
import uvicorn
from starlette.responses import HTMLResponse
from database import add_user, get_user, add_session, get_session, del_session, get_user_by_id

app = FastAPI()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

sessions = {}


class LoginSchema(BaseModel):
    username: str
    password: str


class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    session_id = request.cookies.get("session_id")
    if get_session(session_id):
        response = RedirectResponse(url="/protected", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="session_id", value=session_id)
        return response
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/protected", response_class=HTMLResponse)
async def protected(request: Request):
    session_id = request.cookies.get("session_id")
    if not get_session(session_id):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("protected.html", {"request": request})


@app.get("/get_data")
async def get_data(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id is not None:
        user = get_user_by_id(get_session(session_id).user_id)
        return {"username": user.username, "email": user.email}
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.post("/register")
async def register(request: Request, credentials: RegisterSchema):
    user = add_user(credentials.username, credentials.email, credentials.password)
    if not user:
        return
    session_id = secrets.token_urlsafe(16)
    add_session(session_id, user.id)

    response = RedirectResponse(url="/protected", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.post("/login")
async def login(request: Request, credentials: LoginSchema):
    user = get_user(credentials.username)
    if not user or user.password != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильное имя пользователя или пароль")
    session_id = secrets.token_urlsafe(16)
    add_session(session_id, user.id)
    response = RedirectResponse(url="/protected", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.get("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    sessions = get_session(session_id)
    if sessions:
        del_session(sessions)
    request.cookies.clear()
    return RedirectResponse(url="/login")


if __name__ == "__main__":
    uvicorn.run(app)
