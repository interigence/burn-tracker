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

def init_db():
    """데이터베이스가 없으면 자동 생성"""
    if not os.path.exists(DB_PATH):
        print("✅ DB 파일이 없습니다. 새로 생성합니다.")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS burn_history (
                txhash TEXT PRIMARY KEY,
                amount REAL,
                timestamp INTEGER
            )
        """)
        conn.commit()
        conn.close()
        print("✅ SQLite 데이터베이스 초기화 완료")

# 앱 시작 시 DB 초기화 실행
init_db()

def fetch_burn_transactions():
    """Etherscan에서 소각 주소로 전송된 트랜잭션 전체 조회 (페이지네이션 적용)"""
    all_transactions = []
    page = 1
    offset = 100  # 한 페이지에 조회할 항목 수

    while True:
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": TOKEN_CONTRACT,
            "address": BURN_ADDRESS,
            "page": page,
            "offset": offset,
            "sort": "desc",
            "apikey": ETHERSCAN_API_KEY
        }
        response = requests.get(API_URL, params=params)
        data = response.json()

        if "result" in data:
            transactions = data["result"]
            if not transactions:
                # 더 이상 가져올 데이터가 없으면 루프 종료
                break

            all_transactions.extend(transactions)

            # 만약 조회된 트랜잭션 수가 offset보다 작으면, 마지막 페이지이므로 종료
            if len(transactions) < offset:
                break

            page += 1
        else:
            break

    return all_transactions


def update_database(transactions):
    """새로운 소각 데이터를 DB에 저장"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
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
        print("✅ DB 업데이트 완료")
    except Exception as e:
        print("❌ DB 업데이트 중 오류 발생: {e}")

def get_total_burned():
    """총 소각량을 데이터베이스에서 조회"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(amount) FROM burn_history")
        total_burned = cursor.fetchone()[0] or 0
        
        conn.close()
        return total_burned
    except Exception as e:
        print("❌ DB 조회 중 오류 발생: {e}")
        return 0  # 오류 발생 시 기본값 0 반환

@app.route('/')
def home():
    return render_template('index.html')  # templates/index.html을 렌더링

@app.route('/api/burned', methods=["GET"])
def burned():
    """소각된 SHIRONEKO 토큰 총량 반환"""
    total_burned = get_total_burned()
    return jsonify({"total_burned": total_burned})

if __name__ == "__main__":
    app.run(debug=True)
