from pydantic import BaseModel


class ReviewBase(BaseModel):
    rating: int
    comment: str | None = None


class ReviewCreate(ReviewBase):
    user_id: int
    menu_item_id: int


class ReviewUpdate(BaseModel):
    rating: int | None = None
    comment: str | None = None


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    menu_item_id: int

    class Config:
        orm_mode = True
