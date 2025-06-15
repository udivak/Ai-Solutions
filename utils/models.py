from pydantic import BaseModel
from typing import Optional, List


class Customer(BaseModel):
    customer_id: int
    customer_name: str
    customer_telephone: str
    customer_city: Optional[str]


class OrderItem(BaseModel):
    item_id: int
    quantity: int


class OrderRequest(BaseModel):
    customer_id: int
    customer_telephone: str
    items: List[OrderItem]


class OrderItemRaw(BaseModel):
    item_name: str
    quantity: int


class OrderRequestRaw(BaseModel):
    customer_id: int
    customer_telephone: str
    items: List[OrderItemRaw]


class OrderIDs(BaseModel):
    order_ids: List[int]


class MessageRequest(BaseModel):
    text: str
    sender: str
    language: str = "he"





class Other(BaseModel):
    query: str

