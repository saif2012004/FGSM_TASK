"""
Test script to verify the live backend is working correctly
"""

import requests
import json
from PIL import Image
import io
import numpy as np

# Configuration - Updated for live backend
API_BASE_URL = "http://16.16.32.175:8000"

def create_test_image():
    """Create a simple test image (28x28 grayscale)"""
    # Create a simple pattern that looks like a digit
    img_array = np.random.rand(28, 28) * 255
    
    # Add some structure to make it look more like a digit
    img_array[8:20, 8:20] = 200  # Bright square in center
    img_array[10:18, 10:18] = 50  # Dark square inside
    
    img = Image.fromarray(img_array.astype(np.uint8), mode='L')
    return img

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing live backend health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_attack_endpoint():
    """Test the FGSM attack endpoint"""
    print("\n🔍 Testing live backend attack endpoint...")
    
    # Create test image
    test_img = create_test_image()
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    test_img.save(img_buffer, format='PNG')
    img_bytes = img_buffer.getvalue()
    
    # Prepare the request
    files = {'file': ('test_image.png', img_bytes, 'image/png')}
    data = {'epsilon': 0.1}
    
    try:
        response = requests.post(f"{API_BASE_URL}/attack", files=files, data=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Attack successful!")
            print(f"Clean Prediction: {result['clean_prediction']}")
            print(f"Adversarial Prediction: {result['adversarial_prediction']}")
            print(f"Attack Success: {result['attack_success']}")
            print(f"Clean Confidence: {result['confidence_clean']:.4f}")
            print(f"Adversarial Confidence: {result['confidence_adversarial']:.4f}")
            print(f"Epsilon Used: {result['epsilon_used']}")
            return True
        else:
            print(f"❌ Attack failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Attack request failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Live Backend")
    print("=" * 50)
    print(f"Backend URL: {API_BASE_URL}")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("❌ Backend health check failed!")
        print("Possible issues:")
        print("1. Backend server is not running")
        print("2. Firewall blocking the connection")
        print("3. Network connectivity issues")
        print("4. Security group not allowing HTTP traffic")
        return
    
    # Test attack endpoint
    attack_ok = test_attack_endpoint()
    
    print("\n" + "=" * 50)
    if health_ok and attack_ok:
        print("✅ All tests passed! Live backend is working correctly.")
        print("🎉 Frontend can now connect to the live backend!")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    print("\n📋 Test Summary:")
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Attack Endpoint: {'✅ PASS' if attack_ok else '❌ FAIL'}")

if __name__ == "__main__":
    main()
