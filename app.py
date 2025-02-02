from flask import Flask, render_template, jsonify
import os
import requests
import sqlite3

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

@app.route('/')
def home():
    return render_template('index.html')  # templates/index.html을 렌더링

@app.route('/api/burned', methods=["GET"])
def burned():
    """소각된 SHIRONEKO 토큰 총량 반환"""
    total_burned = fetch_total_burned()  # Etherscan에서 직접 조회
    return jsonify({"total_burned": total_burned})

if __name__ == "__main__":
    app.run(debug=True)
