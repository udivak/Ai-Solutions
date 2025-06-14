from fastapi import APIRouter, HTTPException
from models import Customer
import data_access

router = APIRouter()

@router.get("/get_customer_info/{customer_telephone}", response_model=Customer)
async def get_customer_info(customer_telephone: str):
    customer = data_access.get_customer_info(customer_telephone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return Customer(**dict(customer))
