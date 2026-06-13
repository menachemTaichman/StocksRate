import os
import json
from datetime import datetime
import requests

def scrape_fund_price(fund_id):
    url = f"https://maya.tase.co.il/api/v1/funds/mutual/{fund_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[-] Failed to fetch fund {fund_id}. Status code: {response.status_code}")
            return None

        data = response.json()
        price = data.get("purchasePrice")
        if price is None:
            print(f"[-] Price not found for fund {fund_id}")
            return None

        return {
            "price": float(price),
            "price_date": data.get("ratesAsOf"),
        }

    except Exception as e:
        print(f"[-] Error parsing fund {fund_id}: {str(e)}")
        return None

def main():
    # טעינת רשימת הקרנות
    if not os.path.exists('funds.json'):
        print("[-] funds.json not found.")
        return
        
    with open('funds.json', 'r', encoding='utf-8') as f:
        funds_list = json.load(f)
        
    # טעינת מחירים קיימים כדי לא לדרוס מידע במקרה של כישלון נקודתי
    prices_data = {}
    if os.path.exists('prices.json'):
        try:
            with open('prices.json', 'r', encoding='utf-8') as f:
                prices_data = json.load(f)
        except Exception:
            pass

    print(f"[+] Starting scrape for {len(funds_list)} funds...")
    
    for fund_id in funds_list:
        result = scrape_fund_price(fund_id)
        if result:
            print(f"[+] Fund {fund_id}: {result['price']} ({result['price_date']})")
            prices_data[str(fund_id)] = {
                "price": result["price"],
                "price_date": result["price_date"],
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
    # שמירה חזרה לקובץ הסטטי
    with open('prices.json', 'w', encoding='utf-8') as f:
        json.dump(prices_data, f, ensure_ascii=False, indent=4)
    print("[+] Scrape process completed and prices.json updated.")

if __name__ == "__main__":
    main()