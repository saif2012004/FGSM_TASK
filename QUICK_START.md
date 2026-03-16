# Quick Start: First 3 Tasks (Start Today!)

This file contains the **first 3 critical tasks** you should do today to start improving the project. These are high-impact, relatively quick tasks that will immediately make the project more functional.

---

## Task 1: Create Model Training Script ⏱️ 2-3 hours

### Why Critical?
Without a trained model, the application won't work for anyone who clones your repository. The `.pth` files are gitignored, so nobody has the weights!

### What to Do

Create `backend/train_mnist_model.py`:

```python
"""
Train a proper MNIST model for FGSM adversarial attack demonstration
This script trains a CNN model and saves the weights
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from fgsm import load_mnist_model
import os

def train_mnist_model(epochs=10, save_path='mnist_model_professional.pth'):
    """
    Train MNIST model with proper training loop
    
    Args:
        epochs: Number of training epochs (default: 10)
        save_path: Where to save model weights
    """
    print("🚀 Starting MNIST Model Training")
    print("=" * 50)
    
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Data transforms with augmentation
    transform_train = transforms.Compose([
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Load MNIST dataset
    print("\n📦 Loading MNIST dataset...")
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform_train)
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform_test)
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False, num_workers=2)
    
    print(f"Training samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    
    # Create model
    print("\n🧠 Creating model...")
    model = load_mnist_model().to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.7)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")
    
    # Training loop
    print("\n🏋️ Training model...")
    best_accuracy = 0.0
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = nn.functional.nll_loss(output, target)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
            
            if batch_idx % 100 == 0:
                print(f'Epoch [{epoch+1}/{epochs}] Batch [{batch_idx}/{len(train_loader)}] '
                      f'Loss: {loss.item():.4f}')
        
        train_accuracy = 100. * correct / total
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation phase
        model.eval()
        test_loss = 0.0
        correct = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                test_loss += nn.functional.nll_loss(output, target, reduction='sum').item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
        
        test_loss /= len(test_loader.dataset)
        test_accuracy = 100. * correct / len(test_loader.dataset)
        
        print(f'\n📊 Epoch {epoch+1}/{epochs} Summary:')
        print(f'   Train Loss: {avg_train_loss:.4f} | Train Acc: {train_accuracy:.2f}%')
        print(f'   Test Loss: {test_loss:.4f} | Test Acc: {test_accuracy:.2f}%')
        print('-' * 50)
        
        # Save best model
        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            torch.save(model.state_dict(), save_path)
            print(f'✅ New best model saved! Accuracy: {best_accuracy:.2f}%')
        
        scheduler.step()
    
    # Final results
    print("\n" + "=" * 50)
    print(f"🎉 Training Complete!")
    print(f"Best Test Accuracy: {best_accuracy:.2f}%")
    print(f"Model saved to: {save_path}")
    print("=" * 50)
    
    return model, best_accuracy

def test_model_on_samples(model_path='mnist_model_professional.pth'):
    """
    Test the trained model on a few samples to verify it works
    """
    print("\n🧪 Testing trained model...")
    
    device = torch.device("cpu")
    model = load_mnist_model()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    
    # Test on 10 random samples
    import random
    indices = random.sample(range(len(test_dataset)), 10)
    
    correct = 0
    print("\nSample predictions:")
    for idx in indices:
        image, label = test_dataset[idx]
        with torch.no_grad():
            output = model(image.unsqueeze(0))
            pred = output.argmax(dim=1).item()
            confidence = torch.softmax(output, dim=1).max().item()
            
            status = "✅" if pred == label else "❌"
            print(f"{status} True: {label}, Predicted: {pred}, Confidence: {confidence:.4f}")
            if pred == label:
                correct += 1
    
    print(f"\nSample accuracy: {correct}/10 ({correct*10}%)")

if __name__ == "__main__":
    # Train the model
    model, accuracy = train_mnist_model(epochs=10)
    
    # Test it
    test_model_on_samples()
    
    print("\n✅ Done! You can now use this model with the FastAPI backend.")
```

### Commands to Run

```bash
cd E:\internship\DEV_NEURON\backend
python train_mnist_model.py
```

### Expected Output
- Training progress with loss decreasing
- Final accuracy >95%
- Model saved as `mnist_model_professional.pth`

### Verification
```bash
# Test that the backend can load it
python app_fgsm.py
# Should see: "✅ Loaded professional MNIST model"
```

---

## Task 2: Add Environment Configuration ⏱️ 30 minutes

### Why Critical?
Right now the API URL is hardcoded. This makes it hard to switch between local development and production.

### What to Do

**1. Create `frontend/.env.example`**

```env
# Backend API Configuration
# For local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production, change to your deployed backend URL
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**2. Create `frontend/.env.local`**

```env
# Local development configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**3. Create `backend/.env.example`**

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Model Configuration
MODEL_PATH=mnist_model_professional.pth
DEVICE=cpu

# CORS Configuration (comma-separated allowed origins)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Development settings
DEBUG=true
LOG_LEVEL=INFO
```

**4. Create `backend/.env`**

```env
HOST=0.0.0.0
PORT=8000
MODEL_PATH=mnist_model_professional.pth
DEVICE=cpu
ALLOWED_ORIGINS=*
DEBUG=true
LOG_LEVEL=INFO
```

**5. Update `backend/app_fgsm.py` to use environment variables**

Add this at the top after imports:

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration from environment
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
MODEL_PATH = os.getenv("MODEL_PATH", "mnist_model_professional.pth")
DEVICE = os.getenv("DEVICE", "cpu")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
```

Update CORS middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Changed from ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**6. Install python-dotenv**

```bash
cd backend
pip install python-dotenv
# Add to requirements.txt
echo python-dotenv==1.0.0 >> requirements.txt
```

**7. Update README.md**

Add a section:

```markdown
### Environment Configuration

#### Backend
Copy `.env.example` to `.env` and configure:

\`\`\`bash
cd backend
cp .env.example .env
# Edit .env with your settings
\`\`\`

#### Frontend
Copy `.env.example` to `.env.local` and configure:

\`\`\`bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your backend URL
\`\`\`
```

### Verification

```bash
# Test that backend uses env vars
cd backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'PORT: {os.getenv(\"PORT\")}')"

# Should output: PORT: 8000
```

---

## Task 3: Set Up GitHub Actions CI/CD ⏱️ 1 hour

### Why Critical?
Automated testing and deployment saves time and prevents bugs. Status badges make your project look professional.

### What to Do

**1. Create `.github/workflows/ci.yml`**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    name: Backend Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          cd backend
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run linting
        run: |
          pip install flake8
          cd backend
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
      
      - name: Run tests (if tests exist)
        run: |
          cd backend
          if [ -d "tests" ]; then
            pytest --cov=. --cov-report=xml --cov-report=term
          else
            echo "No tests directory found, skipping tests"
          fi
        continue-on-error: true

  frontend-build:
    name: Frontend Build
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run linting
        run: |
          cd frontend
          npm run lint
        continue-on-error: true
      
      - name: Build application
        run: |
          cd frontend
          npm run build
        env:
          NEXT_PUBLIC_API_URL: http://localhost:8000

  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Check file sizes
        run: |
          echo "Checking for large files..."
          find . -type f -size +10M -not -path "*/node_modules/*" -not -path "*/.git/*"
      
      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
        continue-on-error: true
```

**2. Create `.github/workflows/deploy.yml` (for future use)**

```yaml
name: Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy-frontend:
    name: Deploy Frontend
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

**3. Update README.md with status badges**

Add at the top of README, after the title:

```markdown
# FGSM Adversarial Attack System

[![CI/CD Pipeline](https://github.com/saif2012004/DevNeuron_FGSM_TASK-/actions/workflows/ci.yml/badge.svg)](https://github.com/saif2012004/DevNeuron_FGSM_TASK-/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
```

**4. Commit and push**

```bash
cd E:\internship\DEV_NEURON
git add .github/
git add README.md
git commit -m "Add CI/CD pipeline with GitHub Actions"
git push origin main
```

**5. Verify it works**

Go to: https://github.com/saif2012004/DevNeuron_FGSM_TASK-/actions

You should see the workflow running!

### Expected Results
- ✅ Green checkmark on GitHub Actions
- ✅ Status badge in README shows "passing"
- ✅ Automated builds on every push

---

## Summary Checklist

After completing these 3 tasks, you should have:

- [x] **Task 1:** Trained MNIST model with >95% accuracy
- [x] **Task 2:** Environment configuration for both frontend and backend
- [x] **Task 3:** CI/CD pipeline with automated testing

**Time Investment:** 3.5 - 4.5 hours  
**Impact:** HIGH - Makes project functional and professional

---

## Next Steps

After completing these tasks:

1. **Clean up repository:**
   ```bash
   # Remove duplicate folders
   git rm -r "Saif ur Rehman_FGSM_AssessmentReport"
   git commit -m "Remove duplicate assessment folder"
   ```

2. **Test locally:**
   ```bash
   # Terminal 1: Backend
   cd backend
   python app_fgsm.py
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

3. **Deploy:**
   - Backend to Railway/Render
   - Frontend to Vercel
   - Update environment variables

4. **Continue with IMPROVEMENT_PLAN.md Phase 2**

---

## Need Help?

### Common Issues

**Issue: Model training fails with CUDA error**
```bash
# Solution: Force CPU training
export CUDA_VISIBLE_DEVICES=""
python train_mnist_model.py
```

**Issue: Frontend can't connect to backend**
```bash
# Check .env.local
cat frontend/.env.local
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000

# Restart frontend
cd frontend
npm run dev
```

**Issue: GitHub Actions failing**
```bash
# Check the logs on GitHub
# Usually due to missing dependencies or linting errors
# Fix locally first, then push
```

### Resources

- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Remember:** These are just the first 3 tasks. Continue with the full IMPROVEMENT_PLAN.md for a complete portfolio-ready project!

Good luck! 🚀
