# VQA Mobile App Deployment Guide

Complete guide for deploying your trained VQA model as a mobile application.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Mobile App (Flutter)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Voice Command (STT) → Question Text               │ │
│  │  2. Camera Capture → Image                            │ │
│  │  3. Send to API (Image + Question)                    │ │
│  │  4. Receive Answer                                    │ │
│  │  5. Text-to-Speech (TTS) → Audio Output               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Receive Image (base64) + Question                 │ │
│  │  2. Preprocess Image                                  │ │
│  │  3. Run VQA Model Inference                           │ │
│  │  4. Return Answer + Confidence                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Backend Deployment (FastAPI)

### 1.1 Create Backend Structure

```bash
mkdir -p backend
cd backend
```

### 1.2 Create FastAPI Server

Create `backend/main.py`:

```python
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from PIL import Image
import io
import base64
from transformers import BlipProcessor, BlipForQuestionAnswering

app = FastAPI(title="VQA API for Visually Impaired")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = "../models/final/blip_vqa_visually_impaired_v1"
processor = BlipProcessor.from_pretrained(model_path)
model = BlipForQuestionAnswering.from_pretrained(model_path).to(device)
model.eval()

class VQARequest(BaseModel):
    image: str  # base64 encoded
    question: str

class VQAResponse(BaseModel):
    answer: str
    confidence: float

@app.get("/")
async def root():
    return {"message": "VQA API is running"}

@app.post("/api/vqa", response_model=VQAResponse)
async def answer_question(request: VQARequest):
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # Process inputs
        inputs = processor(
            images=image,
            text=request.question,
            return_tensors="pt"
        ).to(device)

        # Generate answer
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=10, num_beams=3)

        # Decode answer
        answer = processor.decode(outputs[0], skip_special_tokens=True)

        # Calculate confidence (simplified)
        confidence = 0.85  # You can implement proper confidence calculation

        return VQAResponse(answer=answer, confidence=confidence)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 1.3 Create Requirements

Create `backend/requirements.txt`:

```txt
fastapi==0.95.0
uvicorn==0.22.0
python-multipart==0.0.6
torch>=2.0.0
transformers>=4.30.0
Pillow>=9.5.0
```

### 1.4 Run Backend

```bash
pip install -r requirements.txt
python main.py
```

Test at: http://localhost:8000/docs

## Phase 2: Mobile App (Flutter)

### 2.1 Create Flutter Project

```bash
flutter create vqa_assistant
cd vqa_assistant
```

### 2.2 Add Dependencies

Edit `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  camera: ^0.10.5
  speech_to_text: ^6.3.0
  flutter_tts: ^3.7.0
  http: ^1.1.0
  image_picker: ^1.0.4
```

### 2.3 Main App Code

Create `lib/main.dart`:

```dart
import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const VQAAssistantApp());
}

class VQAAssistantApp extends StatelessWidget {
  const VQAAssistantApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VQA Assistant',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
```

### 2.4 Home Screen

Create `lib/screens/home_screen.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../services/vqa_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late CameraController _cameraController;
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  final VQAService _vqaService = VQAService();

  bool _isListening = false;
  String _question = '';
  String _answer = '';

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _initializeSpeech();
  }

  Future<void> _initializeCamera() async {
    final cameras = await availableCameras();
    _cameraController = CameraController(
      cameras.first,
      ResolutionPreset.medium,
    );
    await _cameraController.initialize();
    setState(() {});
  }

  Future<void> _initializeSpeech() async {
    await _speechToText.initialize();
  }

  Future<void> _startListening() async {
    await _speechToText.listen(
      onResult: (result) {
        setState(() {
          _question = result.recognizedWords;
        });
      },
    );
    setState(() => _isListening = true);
  }

  Future<void> _stopListening() async {
    await _speechToText.stop();
    setState(() => _isListening = false);

    // Process question
    if (_question.isNotEmpty) {
      await _processQuestion();
    }
  }

  Future<void> _processQuestion() async {
    // Capture image
    final image = await _cameraController.takePicture();

    // Send to API
    final response = await _vqaService.askQuestion(
      imagePath: image.path,
      question: _question,
    );

    setState(() {
      _answer = response['answer'];
    });

    // Speak answer
    await _flutterTts.speak(_answer);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('VQA Assistant'),
      ),
      body: Column(
        children: [
          // Camera preview
          if (_cameraController.value.isInitialized)
            Expanded(
              child: CameraPreview(_cameraController),
            ),

          // Question display
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              _question.isEmpty ? 'Tap to ask a question' : _question,
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),

          // Answer display
          if (_answer.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'Answer: $_answer',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
            ),

          // Microphone button
          Padding(
            padding: const EdgeInsets.all(32.0),
            child: FloatingActionButton.large(
              onPressed: _isListening ? _stopListening : _startListening,
              child: Icon(_isListening ? Icons.mic : Icons.mic_none),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _cameraController.dispose();
    super.dispose();
  }
}
```

### 2.5 VQA Service

Create `lib/services/vqa_service.dart`:

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class VQAService {
  final String baseUrl = 'http://YOUR_SERVER_IP:8000';

  Future<Map<String, dynamic>> askQuestion({
    required String imagePath,
    required String question,
  }) async {
    // Read image
    final bytes = await File(imagePath).readAsBytes();
    final base64Image = base64Encode(bytes);

    // Make API request
    final response = await http.post(
      Uri.parse('$baseUrl/api/vqa'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'image': base64Image,
        'question': question,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get answer');
    }
  }
}
```

## Phase 3: Deployment

### 3.1 Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t vqa-backend .
docker run -p 8000:8000 vqa-backend
```

### 3.2 Cloud Deployment Options

#### AWS EC2 with GPU

```bash
# Launch p2.xlarge instance
# Install CUDA and PyTorch
# Deploy with Docker
```

#### Google Cloud Run

```bash
gcloud run deploy vqa-backend \
  --source . \
  --platform managed \
  --region us-central1
```

## Testing

### Test Backend

```bash
curl -X POST http://localhost:8000/api/vqa \
  -H "Content-Type: application/json" \
  -d '{"image": "BASE64_IMAGE", "question": "What color is this?"}'
```

### Test Mobile App

1. Update `baseUrl` in `vqa_service.dart`
2. Run: `flutter run`
3. Test voice commands and image capture

## Success Criteria

- ✅ Backend API responds to VQA requests
- ✅ Mobile app captures images
- ✅ STT converts voice to text
- ✅ TTS speaks answers
- ✅ End-to-end flow works smoothly

---

**Your VQA system is now ready to help visually impaired users! 🎉**
