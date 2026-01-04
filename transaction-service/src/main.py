from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2 import OperationalError

app = FastAPI(title="Transaction Service", version="1.0")

# --- Database connection ---
try:
    conn = psycopg2.connect(
        host="newbank-db",  # Docker container name
        database="postgres",
        user="postgres",
        password="supersecret",
        port=5432
    )
except OperationalError as e:
    print(f"Error connecting to the database: {e}")
    conn = None

# --- Health endpoint ---
@app.get("/health")
def health():
    if conn:
        return {"status": "ok", "service": "transaction-service"}
    else:
        return {"status": "error", "service": "transaction-service", "detail": "DB connection failed"}

# --- Get recent transactions for a specific account ---
@app.get("/transactions/{account_id}")
def read_transactions(account_id: str):
    if not conn:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    cur = conn.cursor()
    cur.execute(
        "SELECT id, amount, type, date, description FROM transactions "
        "WHERE account_id = %s ORDER BY date DESC LIMIT 10",
        (account_id,)
    )
    rows = cur.fetchall()
    cur.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No transactions found for account {account_id}")

    return {
        "account_id": account_id,
        "recent_transactions": [
            {
                "id": r[0],
                "amount": float(r[1]),
                "type": r[2],
                "date": str(r[3]),
                "description": r[4]
            }
            for r in rows
        ]
    }

# --- Get all transactions (optional) ---
@app.get("/transactions")
def get_all_transactions():
    if not conn:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    cur = conn.cursor()
    cur.execute(
        "SELECT id, account_id, amount, type, date, description FROM transactions ORDER BY date DESC LIMIT 50"
    )
    rows = cur.fetchall()
    cur.close()

    return [
        {
            "id": r[0],
            "account_id": r[1],
            "amount": float(r[2]),
            "type": r[3],
            "date": str(r[4]),
            "description": r[5]
        }
        for r in rows
    ]
