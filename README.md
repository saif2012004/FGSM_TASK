# FGSM Adversarial Attack System

A comprehensive implementation of Fast Gradient Sign Method (FGSM) adversarial attacks with a FastAPI backend and Next.js frontend, developed for the DevNeuron Software Engineer Intern Assessment.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Local Development](#local-development)
- [API Documentation](#api-documentation)
- [Frontend Features](#frontend-features)
- [FGSM Explanation](#fgsm-explanation)
- [Observations](#observations)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Screenshots](#screenshots)

## 🎯 Overview

This project demonstrates adversarial attacks on machine learning models using the Fast Gradient Sign Method (FGSM). It provides an interactive web interface where users can upload images, adjust attack parameters, and observe how small perturbations can fool neural networks.

## ✨ Features

- **Interactive Web Interface**: Upload images and see real-time adversarial attack results
- **Adjustable Attack Strength**: Control epsilon parameter with slider interface
- **Visual Comparison**: Side-by-side display of original vs adversarial images
- **Attack Analysis**: Shows prediction changes, confidence scores, and success status
- **RESTful API**: FastAPI backend with comprehensive endpoint documentation
- **Responsive Design**: Modern UI built with Next.js and Tailwind CSS

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   Next.js       │ ◄──────────────► │   FastAPI       │
│   Frontend      │                  │   Backend       │
│                 │                  │                 │
│ - Image Upload  │                  │ - FGSM Attack   │
│ - Epsilon Ctrl  │                  │ - ML Model      │
│ - Results View  │                  │ - Image Proc.   │
└─────────────────┘                  └─────────────────┘
        │                                     │
        │                                     │
        v                                     v
┌─────────────────┐                  ┌─────────────────┐
│   AWS Amplify   │                  │ AWS Lambda /    │
│   (Frontend)    │                  │ EC2 (Backend)   │
└─────────────────┘                  └─────────────────┘
```

## ⚙️ Setup Instructions

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control

### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create demo model (for testing):**

   ```bash
   python train_demo_model.py
   ```

4. **Start the FastAPI server:**

   ```bash
   uvicorn app_fgsm:app --host 0.0.0.0 --port 8000 --reload
   ```

   The API will be available at: `http://localhost:8000`
   API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm run dev
   ```

   The frontend will be available at: `http://localhost:3000`

## 🚀 Local Development

### Running Both Services

1. **Terminal 1 - Backend:**

   ```bash
   cd backend
   uvicorn app_fgsm:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Terminal 2 - Frontend:**

   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Environment Configuration

The frontend uses environment variables for API configuration:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production deployment, update this to your deployed backend URL.

## 📡 API Documentation

### Health Check

```http
GET /health
```

Returns the health status of the API and model loading status.

### Generate Adversarial Attack

```http
POST /attack
```

**Parameters:**

- `file` (form-data): Image file (PNG/JPEG)
- `epsilon` (form-data): Attack strength (0.0 - 1.0, default: 0.1)

**Response:**

```json
{
  "clean_prediction": 7,
  "adversarial_prediction": 2,
  "adversarial_image": "base64_encoded_image_string",
  "attack_success": true,
  "confidence_clean": 0.95,
  "confidence_adversarial": 0.87,
  "epsilon_used": 0.1
}
```

## 🎨 Frontend Features

- **File Upload**: Drag-and-drop or click to upload images
- **Epsilon Control**: Slider to adjust attack strength (0.00 - 0.50)
- **Real-time Results**: Immediate display of attack results
- **Image Comparison**: Side-by-side original vs adversarial images
- **Attack Analysis**: Success status, prediction changes, confidence scores
- **Educational Content**: Explanation of FGSM methodology
- **Responsive Design**: Works on desktop and mobile devices

## 🧠 FGSM Explanation

The Fast Gradient Sign Method (FGSM) is a fundamental adversarial attack technique developed by Goodfellow et al. It generates adversarial examples by making small, carefully crafted perturbations to input images that cause machine learning models to misclassify them.

### Mathematical Formulation

The FGSM attack follows this formula:

**x_adversarial = x_original + ε × sign(∇_x J(θ, x, y))**

Where:

- `x_original` is the original input image
- `ε` (epsilon) controls the magnitude of perturbation
- `∇_x J(θ, x, y)` is the gradient of the loss function with respect to the input
- `sign()` function extracts the direction of the gradient

### How It Works

1. **Forward Pass**: The model processes the original image and makes a prediction
2. **Loss Calculation**: Compute the loss between the prediction and true label
3. **Gradient Computation**: Calculate gradients of the loss with respect to input pixels
4. **Perturbation Generation**: Take the sign of gradients and scale by epsilon
5. **Adversarial Example**: Add the perturbation to the original image

The key insight is that neural networks are vulnerable to small, imperceptible changes in the input that align with the gradient direction of the loss function.

## 📊 Observations

### Attack Effectiveness

Through testing with various epsilon values, we observed:

1. **Epsilon = 0.05-0.1**: Subtle perturbations, moderate attack success
2. **Epsilon = 0.15-0.25**: Stronger attacks, higher success rate but more visible changes
3. **Epsilon = 0.3+**: Very effective attacks but significant visual distortion

### Prediction Changes

- **Lower Epsilon**: Attacks may fail but cause confidence drops
- **Higher Epsilon**: More likely to cause misclassification
- **Model Dependency**: Success varies significantly based on model architecture

### Visual Impact

- Small epsilon values create imperceptible changes to human eyes
- Larger epsilon values create visible noise but still fool the model
- The trade-off between attack strength and visual quality is crucial

### Key Findings

1. **Vulnerability Demonstration**: Even simple models are susceptible to FGSM attacks
2. **Epsilon Sensitivity**: Small changes in epsilon can dramatically affect attack success
3. **Confidence Impact**: Even failed attacks often reduce model confidence
4. **Universality**: FGSM works across different types of images and models

## 🌐 Deployment

### Backend Deployment Options

#### Option A: AWS Lambda (Recommended)

- **Service**: AWS Lambda + API Gateway
- **Benefits**: Serverless, auto-scaling, cost-effective
- **Free Tier**: Covered under Always Free tier

#### Option B: AWS EC2

- **Service**: EC2 t2.micro instance
- **Benefits**: Full control, persistent storage
- **Free Tier**: 12-month free tier eligible

### Frontend Deployment

#### AWS Amplify (Recommended)

- **Service**: AWS Amplify Hosting
- **Benefits**: CDN, automatic builds, SSL
- **Free Tier**: 1,000 build minutes, 5GB storage, 15GB served

### Deployment Commands

**Backend (Lambda):**

```bash
# Package the application
zip -r fgsm-backend.zip .

# Deploy using AWS CLI or Console
aws lambda create-function --function-name fgsm-backend
```

**Frontend (Amplify):**

```bash
# Build for production
npm run build

# Deploy to Amplify
amplify init
amplify add hosting
amplify publish
```

## 📁 Project Structure

```
DEV_NEURON/
├── backend/
│   ├── app_fgsm.py              # FastAPI application
│   ├── fgsm.py                  # FGSM attack implementation
│   ├── train_demo_model.py      # Demo model creation
│   ├── requirements.txt         # Python dependencies
│   └── mnist_model.pth         # Pre-trained model weights
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx        # Main application component
│   │       ├── layout.tsx      # App layout
│   │       └── globals.css     # Global styles
│   ├── .env.local              # Environment variables
│   ├── package.json            # Node.js dependencies
│   └── next.config.js          # Next.js configuration
└── README.md                   # Project documentation
```

## 🛠️ Technologies Used

### Backend

- **FastAPI**: Modern Python web framework
- **PyTorch**: Deep learning framework
- **Uvicorn**: ASGI server
- **Pillow**: Image processing
- **NumPy**: Numerical computations

### Frontend

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls

### Deployment

- **AWS Amplify**: Frontend hosting
- **AWS Lambda**: Serverless backend
- **AWS API Gateway**: API management
- **AWS EC2**: Alternative backend hosting

## 📸 Screenshots

### Main Interface

![Main Interface](docs/screenshots/main-interface.png)
_Interactive FGSM attack interface with file upload and epsilon control_

### Attack Results

![Attack Results](docs/screenshots/attack-results.png)
_Side-by-side comparison showing successful adversarial attack_

### API Documentation

![API Docs](docs/screenshots/api-docs.png)
_FastAPI automatic documentation interface_

## 🎓 Educational Value

This project demonstrates several important concepts in AI security:

1. **Adversarial Vulnerability**: Shows how ML models can be fooled
2. **Attack Methodology**: Implements a fundamental attack technique
3. **Defense Awareness**: Highlights the need for robust AI systems
4. **Practical Implementation**: Provides hands-on experience with adversarial ML

## 🔧 Development Notes

### Model Considerations

- The demo uses a simple CNN for MNIST-style images
- In production, you would use properly trained, robust models
- The current implementation is for educational/demonstration purposes

### Performance Optimizations

- Backend uses CPU-only PyTorch for compatibility
- Frontend implements proper error handling and loading states
- Images are processed and returned as base64 for simplicity

### Security Considerations

- File upload validation prevents malicious files
- API includes proper error handling and input validation
- CORS is configured for development (should be restricted in production)

## 📞 Contact

This project was developed as part of the DevNeuron Software Engineer Intern Assessment.

**Submission Details:**

- **Assessment**: Software Engineer Intern Position
- **Company**: DevNeuron
- **Submission**: Complete implementation with deployment

---

**Note**: This is an educational project demonstrating adversarial attacks. In real-world applications, such techniques should only be used for research, security testing, and improving model robustness.
