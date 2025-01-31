import os
import requests
import sqlite3
import time

# Etherscan API 설정
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
TOKEN_CONTRACT = "0xb0AC2b5a73da0e67A8e5489Ba922B3f8d582e058"
BURN_ADDRESS = "0xdEAD000000000000000042069420694206942069"
API_URL = "https://api.etherscan.io/api"

if not ETHERSCAN_API_KEY:
    raise ValueError("🚨 ERROR: 환경 변수 'ETHERSCAN_API_KEY'가 설정되지 않았습니다!")

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

def get_total_burned():
    """총 소각량을 데이터베이스에서 조회"""
    conn = sqlite3.connect("burn_data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount) FROM burn_history")
    total_burned = cursor.fetchone()[0] or 0
    
    conn.close()
    return total_burned
