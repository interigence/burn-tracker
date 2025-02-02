from flask import Flask, render_template, jsonify
import os
import requests
import sqlite3
import time

# Etherscan API 설정
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
TOKEN_CONTRACT = "0xb0AC2b5a73da0e67A8e5489Ba922B3f8d582e058"
BURN_ADDRESS = "0xdEAD000000000000000042069420694206942069"
API_URL = "https://api.etherscan.io/api"

# SQLite 데이터베이스 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "burn_data.db")

app = Flask(__name__)

def fetch_total_burned():
    """Etherscan API에서 소각 주소(BURN_ADDRESS)의 보유 잔액 조회 (총 소각량)"""
    params = {
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": TOKEN_CONTRACT,
        "address": BURN_ADDRESS,
        "tag": "latest",
        "apikey": ETHERSCAN_API_KEY
    }
    
    response = requests.get(API_URL, params=params)
    data = response.json()

    if "result" in data:
        balance = int(data["result"]) / (10 ** 18)  # 소수점 변환
        print(f"🔥 Total Burned Tokens: {balance} SHIRONEKO")
        return balance
    print("❌ Etherscan API 응답 오류:", data)
    return 0  # 에러 발생 시 0 반환

def fetch_burn_rate():
    """24시간 동안의 Burn Rate 계산"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 현재 시간과 24시간 전 시간 계산
    current_time = int(time.time())
    past_24hrs_time = current_time - 86400  # 24시간 전 (초 단위)

    # 현재 Total Burn 조회
    current_total_burned = fetch_total_burned()

    # 24시간 전 Total Burn 조회
    cursor.execute("SELECT amount FROM burn_history WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (past_24hrs_time,))
    past_total_burned = cursor.fetchone()

    if past_total_burned is None:
        past_total_burned = 0
    else:
        past_total_burned = past_total_burned[0]

    conn.close()

    # Burn Amount 계산
    burn_amount_24h = current_total_burned - past_total_burned

    # Burn Rate 계산
    if past_total_burned > 0:
        burn_rate = (burn_amount_24h / past_total_burned) * 100
    else:
        burn_rate = 0  # 데이터 부족 시 0%

    return {"burn_rate": burn_rate, "burn_amount_24h": burn_amount_24h}

@app.route('/api/burned', methods=["GET"])
def burned():
    """소각된 SHIRONEKO 토큰 총량 반환"""
    total_burned = fetch_total_burned()
    return jsonify({"total_burned": total_burned})

@app.route('/api/burn-rate', methods=["GET"])
def burn_rate():
    """24시간 Burn Rate 반환"""
    data = fetch_burn_rate()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
