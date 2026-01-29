"""
Examine VQA v2 Dataset Structure
"""

import json
import os

# Check files
files = ['v2_OpenEnded_mscoco_val2014_questions.json', 'v2_mscoco_val2014_annotations.json']

for file in files:
    if os.path.exists(file):
        size_mb = os.path.getsize(file) / (1024 * 1024)
        print(f"\n{file}: {size_mb:.2f} MB")
        
        with open(file, 'r') as f:
            data = json.load(f)
        
        if 'questions' in data:
            print(f"  Total questions: {len(data['questions'])}")
            print(f"  Sample question: {json.dumps(data['questions'][0], indent=2)}")
        
        if 'annotations' in data:
            print(f"  Total annotations: {len(data['annotations'])}")
            print(f"  Sample annotation: {json.dumps(data['annotations'][0], indent=2)}")
    else:
        print(f"\n{file}: NOT FOUND")
