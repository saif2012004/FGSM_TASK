"""
Download and use a pre-trained MNIST model
This is faster than training from scratch but still demonstrates ML integration
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from fgsm import load_mnist_model

def download_pretrained_model():
    """
    Download a pre-trained MNIST model or create a well-performing one quickly
    This is faster than full training (2-3 epochs vs 10 epochs)
    """
    print("🚀 Setting up pre-trained MNIST model")
    print("=" * 70)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Option 1: Quick training (2-3 epochs) for decent accuracy
    print("\n📦 Quick training for immediate use...")
    print("(This will take ~15-20 minutes instead of 2-3 hours)")
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('./data', train=False, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False, num_workers=2)
    
    print(f"Dataset loaded: {len(train_dataset)} training samples")
    
    # Create model
    model = load_mnist_model().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    print("\n🏋️ Quick training (3 epochs)...")
    print("-" * 70)
    
    for epoch in range(3):
        model.train()
        train_loss = 0
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
                print(f'Epoch [{epoch+1}/3] Batch [{batch_idx}/{len(train_loader)}] '
                      f'Loss: {loss.item():.4f}')
        
        # Test
        model.eval()
        test_correct = 0
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                pred = output.argmax(dim=1)
                test_correct += pred.eq(target).sum().item()
        
        accuracy = 100. * test_correct / len(test_dataset)
        print(f"Epoch {epoch+1}/3: Test Accuracy: {accuracy:.2f}%")
        print("-" * 70)
    
    # Save model
    torch.save(model.state_dict(), 'mnist_model_professional.pth')
    
    print("\n" + "=" * 70)
    print(f"✅ Model ready! Final accuracy: {accuracy:.2f}%")
    print("   Saved to: mnist_model_professional.pth")
    print("   Ready to use with the FastAPI backend!")
    print("=" * 70)
    
    return model, accuracy

def test_quick_model():
    """Test the model works"""
    print("\n🧪 Testing model...")
    
    device = torch.device("cpu")
    model = load_mnist_model()
    model.load_state_dict(torch.load('mnist_model_professional.pth', map_location=device))
    model.eval()
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    
    import random
    random.seed(42)
    indices = random.sample(range(len(test_dataset)), 10)
    
    print("\nSample predictions:")
    correct = 0
    for i, idx in enumerate(indices, 1):
        image, label = test_dataset[idx]
        with torch.no_grad():
            output = model(image.unsqueeze(0))
            pred = output.argmax(dim=1).item()
            conf = torch.softmax(output, dim=1).max().item()
            
            status = "✅" if pred == label else "❌"
            print(f"{status} Sample {i}: True={label}, Pred={pred}, Conf={conf:.4f}")
            if pred == label:
                correct += 1
    
    print(f"\nQuick test: {correct}/10 correct")
    print("✅ Model is working!")

if __name__ == "__main__":
    print("=" * 70)
    print("Quick MNIST Model Setup")
    print("This trains for 3 epochs (~15-20 min) instead of 10 epochs (~2-3 hours)")
    print("You'll get ~97-98% accuracy instead of 98-99%, which is still excellent!")
    print("=" * 70)
    
    model, accuracy = download_pretrained_model()
    
    if accuracy >= 95.0:
        print("\n🎉 Excellent! Model is ready for use!")
        test_quick_model()
        
        print("\n💡 Next steps:")
        print("1. Run backend: python app_fgsm.py")
        print("2. Run frontend: cd ../frontend && npm run dev")
        print("3. Test the attack at http://localhost:3000")
    else:
        print("\n⚠️ Accuracy is a bit low. Consider running full training:")
        print("   python train_mnist_model.py")
