from fastapi import FastAPI
import mysql.connector

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/getOrders/{customer_id}")
async def get_orders(customer_id: int):
    print("in getOrders")
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="160199",
        database="Ai Direct"
    )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Orders WHERE customer_id = %s", (customer_id,))
    result = cursor.fetchall()
    db.close()
    print(result)
    return result
