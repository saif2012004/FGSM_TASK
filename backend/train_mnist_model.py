"""
Train a proper MNIST model for FGSM adversarial attack demonstration
This script trains a CNN model and saves the weights for use with the FastAPI backend
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from fgsm import load_mnist_model
import os
from datetime import datetime


def train_mnist_model(epochs=10, save_path='mnist_model_professional.pth'):
    """
    Train MNIST model with proper training loop
    
    Args:
        epochs: Number of training epochs (default: 10)
        save_path: Where to save model weights
        
    Returns:
        Tuple of (model, best_accuracy)
    """
    print("=" * 70)
    print("Starting MNIST Model Training")
    print("=" * 70)
    print(f"Training started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Data transforms with augmentation for training
    transform_train = transforms.Compose([
        transforms.RandomRotation(10),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Load MNIST dataset
    print("\nLoading MNIST dataset...")
    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform_train)
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform_test)
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False, num_workers=2)
    
    print(f"Training samples: {len(train_dataset):,}")
    print(f"Test samples: {len(test_dataset):,}")
    print(f"Batch size: 64")
    print(f"Training batches: {len(train_loader)}")
    
    # Create model
    print("\nCreating model...")
    model = load_mnist_model().to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.7)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    
    # Training loop
    print("\nTraining model...")
    print("-" * 70)
    best_accuracy = 0.0
    best_epoch = 0
    
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
            
            # Print progress every 100 batches
            if batch_idx % 100 == 0:
                progress = 100. * batch_idx / len(train_loader)
                print(f'Epoch [{epoch+1}/{epochs}] Batch [{batch_idx:3d}/{len(train_loader)}] '
                      f'({progress:5.1f}%) Loss: {loss.item():.4f}')
        
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
        
        # Print epoch summary
        print("-" * 70)
        print(f'Epoch {epoch+1}/{epochs} Summary:')
        print(f'   Training   - Loss: {avg_train_loss:.4f} | Accuracy: {train_accuracy:.2f}%')
        print(f'   Validation - Loss: {test_loss:.4f} | Accuracy: {test_accuracy:.2f}%')
        
        # Save best model
        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            best_epoch = epoch + 1
            torch.save(model.state_dict(), save_path)
            print(f'   [BEST] New best model saved! (Epoch {best_epoch}, Accuracy: {best_accuracy:.2f}%)')
        
        print("-" * 70)
        
        # Update learning rate
        scheduler.step()
        current_lr = scheduler.get_last_lr()[0]
        print(f'   Learning rate: {current_lr:.6f}\n')
    
    # Final results
    print("=" * 70)
    print(f"Training Complete!")
    print(f"Best Epoch: {best_epoch}/{epochs}")
    print(f"Best Test Accuracy: {best_accuracy:.2f}%")
    print(f"Model saved to: {save_path}")
    print(f"Training completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return model, best_accuracy


def test_model_on_samples(model_path='mnist_model_professional.pth', num_samples=20):
    """
    Test the trained model on random samples to verify it works
    
    Args:
        model_path: Path to saved model weights
        num_samples: Number of random samples to test
    """
    print("\nTesting trained model on random samples...")
    print("-" * 70)
    
    device = torch.device("cpu")
    model = load_mnist_model()
    
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"[OK] Model loaded successfully from {model_path}")
    except FileNotFoundError:
        print(f"[ERROR] Model file not found at {model_path}")
        return
    
    model.eval()
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    
    # Test on random samples
    import random
    random.seed(42)  # For reproducibility
    indices = random.sample(range(len(test_dataset)), num_samples)
    
    correct = 0
    predictions = []
    
    print("\nSample predictions:")
    print("-" * 70)
    print(f"{'#':>3} | {'True':>5} | {'Pred':>5} | {'Confidence':>10} | {'Status':>6}")
    print("-" * 70)
    
    for i, idx in enumerate(indices, 1):
        image, label = test_dataset[idx]
        with torch.no_grad():
            output = model(image.unsqueeze(0))
            probabilities = torch.softmax(output, dim=1)
            pred = output.argmax(dim=1).item()
            confidence = probabilities.max().item()
            
            status = "[OK]" if pred == label else "[FAIL]"
            print(f"{i:3d} | {label:5d} | {pred:5d} | {confidence:9.4f} | {status:>6}")
            
            predictions.append({
                'true': label,
                'pred': pred,
                'confidence': confidence,
                'correct': pred == label
            })
            
            if pred == label:
                correct += 1
    
    print("-" * 70)
    accuracy = 100. * correct / num_samples
    print(f"Sample accuracy: {correct}/{num_samples} ({accuracy:.1f}%)")
    print(f"Average confidence: {sum(p['confidence'] for p in predictions) / len(predictions):.4f}")
    print("-" * 70)
    
    # Per-digit accuracy
    digit_stats = {i: {'correct': 0, 'total': 0} for i in range(10)}
    for p in predictions:
        digit = p['true']
        digit_stats[digit]['total'] += 1
        if p['correct']:
            digit_stats[digit]['correct'] += 1
    
    print("\nPer-digit statistics:")
    print(f"{'Digit':>5} | {'Tested':>6} | {'Correct':>7} | {'Accuracy':>8}")
    print("-" * 50)
    for digit in range(10):
        if digit_stats[digit]['total'] > 0:
            acc = 100. * digit_stats[digit]['correct'] / digit_stats[digit]['total']
            print(f"{digit:5d} | {digit_stats[digit]['total']:6d} | "
                  f"{digit_stats[digit]['correct']:7d} | {acc:7.1f}%")
    
    print("-" * 50)
    print("\n[DONE] Model testing complete!")


def evaluate_model_robustness(model_path='mnist_model_professional.pth'):
    """
    Evaluate model robustness against FGSM attacks
    
    Args:
        model_path: Path to saved model weights
    """
    print("\nEvaluating model robustness against FGSM attacks...")
    print("-" * 70)
    
    from fgsm import Attack
    
    device = torch.device("cpu")
    model = load_mnist_model()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    attack = Attack(model, device='cpu')
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
    
    # Test with different epsilon values
    epsilon_values = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    num_test_samples = 100
    
    import random
    random.seed(42)
    test_indices = random.sample(range(len(test_dataset)), num_test_samples)
    
    results = {}
    
    print(f"Testing on {num_test_samples} random samples...")
    print(f"\n{'Epsilon':>7} | {'Accuracy':>8} | {'Attack Success':>14} | {'Avg Conf':>8}")
    print("-" * 50)
    
    for epsilon in epsilon_values:
        correct = 0
        attack_success = 0
        confidences = []
        
        for idx in test_indices:
            image, label = test_dataset[idx]
            image = image.unsqueeze(0)
            target = torch.tensor([label])
            
            if epsilon == 0.0:
                # Clean accuracy
                with torch.no_grad():
                    output = model(image)
                    pred = output.argmax(dim=1).item()
                    conf = torch.softmax(output, dim=1).max().item()
            else:
                # Adversarial attack
                adv_image, _ = attack.generate(image, target, epsilon)
                with torch.no_grad():
                    clean_output = model(image)
                    clean_pred = clean_output.argmax(dim=1).item()
                    
                    adv_output = model(adv_image)
                    pred = adv_output.argmax(dim=1).item()
                    conf = torch.softmax(adv_output, dim=1).max().item()
                    
                    if clean_pred != pred:
                        attack_success += 1
            
            if pred == label:
                correct += 1
            confidences.append(conf)
        
        accuracy = 100. * correct / num_test_samples
        attack_rate = 100. * attack_success / num_test_samples if epsilon > 0 else 0.0
        avg_conf = sum(confidences) / len(confidences)
        
        results[epsilon] = {
            'accuracy': accuracy,
            'attack_success_rate': attack_rate,
            'avg_confidence': avg_conf
        }
        
        print(f"{epsilon:7.2f} | {accuracy:7.1f}% | {attack_rate:13.1f}% | {avg_conf:8.4f}")
    
    print("-" * 50)
    print("\n[DONE] Robustness evaluation complete!")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    epochs = 10
    if len(sys.argv) > 1:
        try:
            epochs = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid epochs value '{sys.argv[1]}', using default: 10")
    
    # Train the model
    print("=" * 70)
    print("MNIST Model Training Script")
    print("For FGSM Adversarial Attack Demonstration")
    print("=" * 70)
    
    model, accuracy = train_mnist_model(epochs=epochs)
    
    if accuracy >= 95.0:
        print("\n[SUCCESS] Excellent! Model achieved >95% accuracy!")
    elif accuracy >= 90.0:
        print("\n[GOOD] Good! Model achieved >90% accuracy!")
    else:
        print("\n[WARNING] Model accuracy is below 90%. Consider training for more epochs.")
    
    # Test the model
    test_model_on_samples()
    
    # Evaluate robustness
    evaluate_model_robustness()
    
    print("\n" + "=" * 70)
    print("[COMPLETE] All done! You can now use this model with the FastAPI backend.")
    print("           The model will be automatically loaded in app_fgsm.py")
    print("=" * 70)
