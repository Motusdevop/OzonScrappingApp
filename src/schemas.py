from typing import Any

from pydantic import BaseModel

from pydantic import HttpUrl

class ParsingSchema(BaseModel):
    search_text: str
    sorting: str
    count_of_cards: int
    offset: int
    # count_of_process: int


class CardSchema(BaseModel):
    title: str
    main_photo: HttpUrl | None
    ozon_card_price: int | None
    discounted_price: int | None
    price: int
    rating: float | None
    count_of_reviews: int
    description: str | None
    deliver_date: str | None
    seller_name: str | None
    seller_url: HttpUrl
    url: HttpUrl

class ResultSchema(BaseModel):
    cards: list[CardSchema]

