"""
Test the exact API call that the frontend is making
"""

import requests
import json
from PIL import Image
import io
import numpy as np

# Same configuration as frontend
API_BASE_URL = "http://16.16.32.175:8000"

def test_exact_frontend_call():
    """Test the exact same call the frontend makes"""
    
    print("🧪 Testing Frontend API Call")
    print("=" * 50)
    print(f"API URL: {API_BASE_URL}/attack")
    
    # Create a test image (same as frontend would send)
    img_array = np.random.rand(28, 28) * 255
    img_array[8:20, 8:20] = 200
    img_array[10:18, 10:18] = 50
    
    img = Image.fromarray(img_array.astype(np.uint8), mode='L')
    
    # Convert to bytes (same format as frontend)
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_bytes = img_buffer.getvalue()
    
    # Prepare request exactly like frontend
    files = {'file': ('test_image.png', img_bytes, 'image/png')}
    data = {'epsilon': 0.1}
    
    # Headers similar to what browser would send
    headers = {
        'Origin': 'http://localhost:3000',
        'Referer': 'http://localhost:3000/',
    }
    
    try:
        print("📤 Sending request...")
        print(f"   - Method: POST")
        print(f"   - URL: {API_BASE_URL}/attack")
        print(f"   - Files: {list(files.keys())}")
        print(f"   - Data: {data}")
        print(f"   - Headers: {headers}")
        
        response = requests.post(
            f"{API_BASE_URL}/attack", 
            files=files, 
            data=data,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📥 Response:")
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   - Response JSON: {json.dumps(result, indent=2)}")
            print("\n✅ API call successful! The issue is likely CORS/browser-related.")
        else:
            print(f"   - Error Response: {response.text}")
            print("\n❌ API call failed!")
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("   - Backend might not be accessible from your network")
    except requests.exceptions.Timeout as e:
        print(f"\n❌ Timeout Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_exact_frontend_call()
