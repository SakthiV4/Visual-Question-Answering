
import requests
import time

PWA_URL = "https://sakthiv4.github.io/Visual-Question-Answering/"

def check_pwa():
    print(f"🌍 Checking PWA URL: {PWA_URL}...")
    for i in range(5):
        try:
            response = requests.get(PWA_URL)
            if response.status_code == 200:
                print("✅ PWA is LIVE and accessible!")
                print(f"📄 Title verified via content length: {len(response.text)} bytes")
                return
            else:
                print(f"⚠️ Status: {response.status_code}. Retrying in 5s... ({i+1}/5)")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(5)
    
    print("❌ Could not verify PWA (might still be building). Please check manually.")

if __name__ == "__main__":
    check_pwa()
