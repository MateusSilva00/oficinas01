from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    username: str
    service_b3: bool = False
    service_bible: bool = False
    service_news: bool = False
    service_soccer: bool = False


class UserUpdateRequest(BaseModel):
    service_b3: bool = False
    service_bible: bool = False
    service_news: bool = False
    service_soccer: bool = False
