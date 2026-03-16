"""
FastAPI application for FGSM adversarial attack demonstration
Provides REST API endpoint for generating adversarial examples
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import io
import base64
import numpy as np
from typing import Optional
import logging
import os
from dotenv import load_dotenv

from fgsm import Attack, load_mnist_model

# Load environment variables
load_dotenv()

# Configuration from environment
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
MODEL_PATH = os.getenv("MODEL_PATH", "mnist_model_professional.pth")
DEVICE = os.getenv("DEVICE", "cpu")
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",")] if ALLOWED_ORIGINS_STR != "*" else ["*"]
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log configuration
logger.info("=" * 70)
logger.info("FGSM Adversarial Attack API - Configuration")
logger.info("=" * 70)
logger.info(f"Host: {HOST}")
logger.info(f"Port: {PORT}")
logger.info(f"Model Path: {MODEL_PATH}")
logger.info(f"Device: {DEVICE}")
logger.info(f"Allowed Origins: {ALLOWED_ORIGINS}")
logger.info(f"Debug Mode: {DEBUG}")
logger.info("=" * 70)

# Initialize FastAPI app
app = FastAPI(
    title="FGSM Adversarial Attack API",
    description="API for generating adversarial examples using Fast Gradient Sign Method",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Configured from environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with origins: {ALLOWED_ORIGINS}")

# Response model
class AttackResponse(BaseModel):
    clean_prediction: int
    adversarial_prediction: int
    adversarial_image: str  # Base64 encoded
    attack_success: bool
    confidence_clean: float
    confidence_adversarial: float
    epsilon_used: float

# Global variables for model and attack
model = None
attack_instance = None
transform = None

def initialize_model():
    """Initialize the model and attack instance"""
    global model, attack_instance, transform
    
    try:
        # Load model architecture
        model = load_mnist_model()
        
        # Try to load model weights from configured path
        try:
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
            logger.info(f"✅ Loaded model weights from {MODEL_PATH}")
        except FileNotFoundError:
            # Try fallback to older model name
            try:
                model.load_state_dict(torch.load('mnist_model.pth', map_location=DEVICE))
                logger.info("✅ Loaded model weights from mnist_model.pth")
            except FileNotFoundError:
                logger.warning("⚠️ No model weights found! Using random initialization.")
                logger.warning("   Run 'python train_mnist_model.py' to train a model.")
        
        model.to(DEVICE)
        model.eval()
        
        # Initialize attack
        attack_instance = Attack(model, device=DEVICE)
        
        # Define image preprocessing pipeline (professional MNIST preprocessing)
        transform = transforms.Compose([
            transforms.Resize((28, 28)),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))  # MNIST standard normalization
        ])
        
        logger.info("✅ Model and attack instance initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize model: {str(e)}")
        raise e

# Initialize on startup
initialize_model()

def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocess uploaded image for model input
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Preprocessed image tensor
    """
    try:
        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary, then to grayscale
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transformations
        image_tensor = transform(image)
        
        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)
        
        return image_tensor
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

def tensor_to_base64(tensor: torch.Tensor) -> str:
    """
    Convert image tensor to base64 string for frontend display
    
    Args:
        tensor: Image tensor
        
    Returns:
        Base64 encoded image string
    """
    try:
        # Remove batch dimension and convert to PIL Image
        tensor = tensor.squeeze(0)
        
        # Convert to numpy and scale to [0, 255]
        numpy_image = tensor.detach().cpu().numpy()
        if numpy_image.shape[0] == 1:  # Grayscale
            numpy_image = numpy_image.squeeze(0)
        
        numpy_image = (numpy_image * 255).astype(np.uint8)
        
        # Convert to PIL Image
        if len(numpy_image.shape) == 2:  # Grayscale
            pil_image = Image.fromarray(numpy_image, mode='L')
        else:
            pil_image = Image.fromarray(numpy_image)
        
        # Convert to base64
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
        
    except Exception as e:
        logger.error(f"Error converting tensor to base64: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "FGSM Adversarial Attack API is running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "attack_initialized": attack_instance is not None
    }

@app.post("/attack", response_model=AttackResponse)
async def generate_adversarial_attack(
    file: UploadFile = File(...),
    epsilon: float = Form(0.1)
):
    """
    Generate adversarial example using FGSM attack
    
    Args:
        file: Uploaded image file (PNG/JPEG)
        epsilon: Attack strength parameter (default: 0.1)
        
    Returns:
        AttackResponse with predictions and adversarial image
    """
    
    # Validate epsilon
    if epsilon < 0 or epsilon > 1.0:
        raise HTTPException(
            status_code=400, 
            detail="Epsilon must be between 0 and 1.0"
        )
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (PNG/JPEG)"
        )
    
    try:
        # Read and preprocess image
        image_bytes = await file.read()
        image_tensor = preprocess_image(image_bytes)
        
        logger.info(f"Processing image with shape: {image_tensor.shape}")
        
        # Get clean prediction
        with torch.no_grad():
            clean_output = model(image_tensor)
            clean_probabilities = F.softmax(clean_output, dim=1)
            clean_prediction = clean_output.argmax(dim=1).item()
            clean_confidence = clean_probabilities.max().item()
        
        logger.info(f"Clean prediction: {clean_prediction} (confidence: {clean_confidence:.4f})")
        
        # For FGSM, we need a target label - we'll use the clean prediction
        target_tensor = torch.tensor([clean_prediction])
        
        # Generate adversarial example
        adversarial_image, attack_success = attack_instance.generate(
            image_tensor, target_tensor, epsilon
        )
        
        # Get adversarial prediction
        with torch.no_grad():
            adv_output = model(adversarial_image)
            adv_probabilities = F.softmax(adv_output, dim=1)
            adversarial_prediction = adv_output.argmax(dim=1).item()
            adv_confidence = adv_probabilities.max().item()
        
        logger.info(f"Adversarial prediction: {adversarial_prediction} (confidence: {adv_confidence:.4f})")
        
        # Convert adversarial image to base64
        adversarial_image_b64 = tensor_to_base64(adversarial_image)
        
        # Determine attack success (prediction changed)
        attack_successful = clean_prediction != adversarial_prediction
        
        logger.info(f"Attack success: {attack_successful}")
        
        return AttackResponse(
            clean_prediction=clean_prediction,
            adversarial_prediction=adversarial_prediction,
            adversarial_image=adversarial_image_b64,
            attack_success=attack_successful,
            confidence_clean=clean_confidence,
            confidence_adversarial=adv_confidence,
            epsilon_used=epsilon
        )
        
    except Exception as e:
        logger.error(f"Error during attack generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating adversarial attack: {str(e)}"
        )

@app.post("/batch_attack")
async def batch_attack_evaluation(epsilon_values: list = None):
    """
    Evaluate model robustness with different epsilon values
    Note: This would require a test dataset in a real implementation
    """
    if epsilon_values is None:
        epsilon_values = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    
    # This is a placeholder - in a real implementation, you would
    # evaluate on a proper test dataset
    results = {}
    for eps in epsilon_values:
        results[f"epsilon_{eps}"] = {
            "description": f"Evaluation with epsilon={eps} would require test dataset"
        }
    
    return {
        "message": "Batch evaluation endpoint - requires test dataset for full implementation",
        "epsilon_values": epsilon_values,
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    
    # For local development
    logger.info(f"Starting server on {HOST}:{PORT}")
    logger.info(f"Reload: {DEBUG}")
    
    uvicorn.run(
        "app_fgsm:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )
