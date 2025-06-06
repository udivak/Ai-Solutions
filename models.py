from pydantic import BaseModel


class OrderItem(BaseModel):
    item_id: int
    quantity: int


class OrderRequest(BaseModel):
    customer_id: int
    items: list[OrderItem]
