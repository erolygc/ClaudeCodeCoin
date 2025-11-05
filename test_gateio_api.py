"""
Gate.io API Test Script
Bu script Gate.io API'nizin çalışıp çalışmadığını kontrol eder
"""

import hashlib
import hmac
import time
import requests
from pathlib import Path
import sys

# Config yolunu ekle
sys.path.insert(0, str(Path(__file__).parent))

# API bilgileri
API_KEY = "5a36b056a39a5b1e6320f0b00be654ca"
SECRET_KEY = "9225a79f6049bfa96cf25a4ca942f2594808d468ce2ce6d512ab857caf9bde1d"
BASE_URL = "https://api.gateio.ws"

def generate_signature(method, url, query_string, payload_string, timestamp):
    """Gate.io API signature oluştur"""
    hashed_payload = hashlib.sha512(payload_string.encode()).hexdigest()
    sign_string = f"{method}\n{url}\n{query_string}\n{hashed_payload}\n{timestamp}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        sign_string.encode(),
        hashlib.sha512
    ).hexdigest()
    return signature

def test_public_api():
    """Public API test (authentication gerektirmez)"""
    print("\n" + "="*70)
    print("[TEST 1] Gate.io Public API Test")
    print("="*70)

    try:
        # BTC_USDT ticker bilgisi al
        url = f"{BASE_URL}/api/v4/spot/tickers"
        params = {"currency_pair": "BTC_USDT"}

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                ticker = data[0]
                print(f"[OK] Public API çalışıyor!")
                print(f"     BTC_USDT Price: ${float(ticker['last']):,.2f}")
                print(f"     24h Volume: ${float(ticker['quote_volume']):,.0f}")
                print(f"     24h Change: {float(ticker['change_percentage']):.2f}%")
                return True
        else:
            print(f"[ERROR] Public API hatası: {response.status_code}")
            print(f"        Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Public API test hatası: {e}")
        return False

def test_private_api():
    """Private API test (authentication gerektirir)"""
    print("\n" + "="*70)
    print("[TEST 2] Gate.io Private API Test (Account Balance)")
    print("="*70)

    try:
        # Account balance endpoint
        method = "GET"
        url_path = "/api/v4/spot/accounts"
        query_string = ""
        payload_string = ""
        timestamp = str(int(time.time()))

        # Signature oluştur
        signature = generate_signature(method, url_path, query_string, payload_string, timestamp)

        # Headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'KEY': API_KEY,
            'Timestamp': timestamp,
            'SIGN': signature
        }

        # Request gönder
        full_url = f"{BASE_URL}{url_path}"
        response = requests.get(full_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Private API çalışıyor!")
            print(f"     API Key geçerli ve authenticated!")
            print(f"\n[ACCOUNT BALANCE]")

            # Bakiyeleri göster (sadece 0'dan büyük olanlar)
            total_assets = 0
            balances_found = False

            for account in data:
                available = float(account.get('available', 0))
                locked = float(account.get('locked', 0))
                total = available + locked

                if total > 0:
                    balances_found = True
                    currency = account.get('currency', 'N/A')
                    print(f"     {currency}: {total:.8f} (Available: {available:.8f}, Locked: {locked:.8f})")

            if not balances_found:
                print("     [INFO] Hesapta bakiye yok (demo/test account olabilir)")

            return True

        elif response.status_code == 401:
            print(f"[ERROR] Authentication hatası!")
            print(f"        API Key veya Secret Key yanlış olabilir")
            print(f"        Response: {response.text}")
            return False
        else:
            print(f"[ERROR] Private API hatası: {response.status_code}")
            print(f"        Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Private API test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_spot_trading_pairs():
    """Spot trading pairs test"""
    print("\n" + "="*70)
    print("[TEST 3] Gate.io Trading Pairs Test")
    print("="*70)

    try:
        url = f"{BASE_URL}/api/v4/spot/currency_pairs"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            pairs = response.json()
            usdt_pairs = [p for p in pairs if p['id'].endswith('_USDT') and p['trade_status'] == 'tradable']

            print(f"[OK] Trading pairs alındı!")
            print(f"     Toplam USDT pairs: {len(usdt_pairs)}")
            print(f"     İlk 10 pair: {', '.join([p['id'] for p in usdt_pairs[:10]])}")
            return True
        else:
            print(f"[ERROR] Trading pairs hatası: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] Trading pairs test hatası: {e}")
        return False

def main():
    print("\n" + "="*70)
    print(" GATE.IO API TEST")
    print("="*70)
    print(f" API Key: {API_KEY}")
    print(f" Base URL: {BASE_URL}")
    print("="*70)

    # Test 1: Public API
    public_ok = test_public_api()

    # Test 2: Private API (Account)
    private_ok = test_private_api()

    # Test 3: Trading Pairs
    pairs_ok = test_spot_trading_pairs()

    # Sonuç
    print("\n" + "="*70)
    print(" TEST SONUÇLARI")
    print("="*70)
    print(f" [{'OK' if public_ok else 'FAIL'}] Public API")
    print(f" [{'OK' if private_ok else 'FAIL'}] Private API (Authentication)")
    print(f" [{'OK' if pairs_ok else 'FAIL'}] Trading Pairs")
    print("="*70)

    if public_ok and private_ok and pairs_ok:
        print("\n[SUCCESS] Gate.io API tamamen çalışıyor! ✅")
        print("          Veri toplama ve trading için kullanılabilir.")
    elif public_ok and not private_ok:
        print("\n[WARNING] Public API çalışıyor ancak Authentication hatası var!")
        print("          API Key veya Secret Key kontrol edilmeli.")
    else:
        print("\n[ERROR] Gate.io API çalışmıyor!")
        print("        Bağlantı veya API ayarlarını kontrol edin.")

    print("\n")

if __name__ == "__main__":
    main()
