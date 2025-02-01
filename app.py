from flask import Flask, render_template, jsonify
import os
import requests
import sqlite3

# Etherscan API 설정
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
TOKEN_CONTRACT = "0xb0AC2b5a73da0e67A8e5489Ba922B3f8d582e058"
BURN_ADDRESS = "0xdEAD000000000000000042069420694206942069"
API_URL = "https://api.etherscan.io/api"

DB_NAME = "burn_data.db"
app = Flask(__name__)

def fetch_burn_transactions():
    """Etherscan에서 소각 주소로 전송된 트랜잭션 조회"""
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": TOKEN_CONTRACT,
        "address": BURN_ADDRESS,
        "page": 1,
        "offset": 100,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    
    if "result" in data:
        return data["result"]
    return []

def update_database(transactions):
    """새로운 소각 데이터를 DB에 저장"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS burn_history (
            txhash TEXT PRIMARY KEY,
            amount REAL,
            timestamp INTEGER
        )
    """)

    for tx in transactions:
        txhash = tx["hash"]
        amount = int(tx["value"]) / (10 ** 18)  # 토큰 소수점 변환
        timestamp = int(tx["timeStamp"])
        
        cursor.execute("""
            INSERT OR IGNORE INTO burn_history (txhash, amount, timestamp) 
            VALUES (?, ?, ?)
        """, (txhash, amount, timestamp))
    
    conn.commit()
    conn.close()

def get_total_burned():
    """총 소각량을 데이터베이스에서 조회"""
    conn = sqlite3.connect("burn_data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount) FROM burn_history")
    total_burned = cursor.fetchone()[0] or 0
    
    conn.close()
    return total_burned

@app.route('/')
def home():
    return render_template('index.html')  # templates/index.html을 렌더링

@app.route('/api/burned', methods=["GET"])
def burned():
    """소각된 SHIRONEKO 토큰 총량 반환"""
    total_burned = get_total_burned()  # 데이터베이스에서 총 소각량 가져오기
    return jsonify({"total_burned": total_burned})  # JSON 형태로 응답 반환

if __name__ == "__main__":
    app.run(debug=True)
