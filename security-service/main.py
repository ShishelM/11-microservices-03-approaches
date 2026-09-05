from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Простейшая база данных в памяти
USERS = {}
VALID_TOKENS = {"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJib2IifQ.hiMVLmssoTsy1MqbmIoviDeFPvo-nCd92d4UFiN2O2I"}

class UserAuth(BaseModel):
    login: str
    password: str

@app.post("/v1/user")
def register(user: UserAuth):
    USERS[user.login] = user.password
    return {"status": "user created"}

@app.post("/v1/token")
def login(user: UserAuth):
    # Упрощенная выдача токена из ДЗ для демонстрации
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJib2IifQ.hiMVLmssoTsy1MqbmIoviDeFPvo-nCd92d4UFiN2O2I"
    return {"token": token}

@app.get("/v1/user")
def get_user(authorization: str = Header(None)):
    return {"login": "bob", "info": "Преподаватель Нетологии"}

@app.get("/v1/token/validation")
def validate_token(authorization: str = Header(None)):
    # Проверка, передан ли токен и валиден ли он
    if not authorization or authorization not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or missing token"
        )
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
