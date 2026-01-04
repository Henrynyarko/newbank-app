from fastapi import FastAPI, HTTPException
import psycopg2
import time

app = FastAPI(title="Account Service", version="1.0")

# --- Database connection with retry ---
for i in range(10):
    try:
        conn = psycopg2.connect(
            host="newbank-db",  # container name of your DB
            database="postgres",
            user="postgres",
            password="supersecret",
            port=5432
        )
        print("✅ Connected to Postgres DB")
        break
    except Exception as e:
        print(f"⚠️ DB not ready, retrying ({i+1}/10)... Error: {e}")
        time.sleep(2)
else:
    raise Exception("❌ Could not connect to Postgres after 10 retries")

# --- Health endpoint ---
@app.get("/health")
def health():
    return {"status": "ok", "service": "account-service"}

# --- Get all accounts ---
@app.get("/accounts")
def get_all_accounts():
    try:
        cur = conn.cursor()
        cur.execute("SELECT account_id, name, balance, currency, created_at FROM accounts")
        rows = cur.fetchall()
        cur.close()

        return [
            {
                "account_id": r[0],
                "name": r[1],
                "balance": float(r[2]),
                "currency": r[3],
                "created_at": str(r[4])
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {e}")

# --- Get specific account ---
@app.get("/accounts/{account_id}")
def read_account(account_id: str):
    try:
        cur = conn.cursor()
        # Fetch account info
        cur.execute(
            "SELECT account_id, name, balance, currency, created_at FROM accounts WHERE account_id = %s",
            (account_id,)
        )
        account_row = cur.fetchone()

        if not account_row:
            cur.close()
            raise HTTPException(status_code=404, detail="Account not found")

        # Fetch recent transactions
        cur.execute(
            "SELECT id, amount, type, date, description FROM transactions WHERE account_id = %s ORDER BY date DESC LIMIT 10",
            (account_id,)
        )
        transactions = cur.fetchall()
        cur.close()

        return {
            "account_id": account_row[0],
            "name": account_row[1],
            "balance": float(account_row[2]),
            "currency": account_row[3],
            "created_at": str(account_row[4]),
            "recent_transactions": [
                {
                    "id": t[0],
                    "amount": float(t[1]),
                    "type": t[2],
                    "date": str(t[3]),
                    "description": t[4]
                }
                for t in transactions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {e}")
