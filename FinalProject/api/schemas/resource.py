from pydantic import BaseModel


class ResourceBase(BaseModel):
    name: str
    amount: float | None = None
    unit: str | None = None


class ResourceCreate(ResourceBase):
    pass


class ResourceResponse(ResourceBase):
    id: int

    class Config:
        orm_mode = True
