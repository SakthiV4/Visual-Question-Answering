
from huggingface_hub import HfApi
import requests
import time

MODEL_REPO = "sakthi04/vqa-model-finetuned"
SPACE_URL = "https://sakthi04-vqa-app.hf.space"

def check_status():
    api = HfApi()
    
    print(f"🔍 Checking Model Repo: {MODEL_REPO}...")
    try:
        files = api.list_repo_files(repo_id=MODEL_REPO, repo_type="model")
        if "model.safetensors" in files:
            print("✅ Model file (model.safetensors) found!")
            print(f"📂 Files found: {len(files)}")
        else:
            print("❌ Model file MISSING in repo!")
    except Exception as e:
        print(f"❌ Error accessing model repo: {e}")

    print(f"\n🌍 Checking Space Status: {SPACE_URL}...")
    try:
        # The Space might still be building, so we allow some retries or just check status
        response = requests.get(f"{SPACE_URL}/")
        if response.status_code == 200:
            print("✅ Space is RUNNING and accessible!")
            print(f"📄 Response: {response.json()}")
        else:
            print(f"⚠️ Space returned status: {response.status_code}")
            print("It might still be building/downloading the model (this takes a few minutes).")
    except Exception as e:
        print(f"❌ Error connecting to Space: {e}")
        print("It is likely still building.")

if __name__ == "__main__":
    check_status()
