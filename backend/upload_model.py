
from huggingface_hub import HfApi, login
import os

# Configuration
MODEL_PATH = "../clean_backup/finetuned_model"  # Path you confirmed
REPO_ID = "sakthi04/vqa-model-finetuned"
TOKEN = os.getenv("HF_TOKEN", "")

def upload_model():
    print("🚀 Starting Model Upload...")
    
    if not TOKEN:
        print("⚠️ Warning: HF_TOKEN environment variable is not set. Assuming you are already logged in via CLI.")
    else:
        # 1. Login (will prompt for token if not saved)
        login(token=TOKEN) # We'll run this interactively or rely on cached token
    
    api = HfApi(token=TOKEN if TOKEN else None)
    
    # 2. Create Repository
    try:
        api.create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True)
        print(f"✅ Repository {REPO_ID} ready.")
    except Exception as e:
        print(f"⚠️ Repo creation warning: {e}")

    # 3. Upload Files
    print(f"📤 Uploading files from {MODEL_PATH}...")
    try:
        api.upload_folder(
            folder_path=MODEL_PATH,
            repo_id=REPO_ID,
            repo_type="model",
            commit_message="Upload fine-tuned model (80.2% accuracy)"
        )
        print("✅ Upload Completed Successfully!")
        print(f"🔗 Model URL: https://huggingface.co/{REPO_ID}")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

if __name__ == "__main__":
    # Ensure huggingface_hub is installed
    try:
        import huggingface_hub
        upload_model()
    except ImportError:
        print("Please run: pip install huggingface_hub")
