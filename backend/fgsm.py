"""
Fast Gradient Sign Method (FGSM) Implementation
Based on Goodfellow et al. "Explaining and Harnessing Adversarial Examples"

FGSM generates adversarial examples by taking a step in the direction of the gradient
of the loss function with respect to the input image.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional


class Attack:
    """
    FGSM Attack Class for generating adversarial examples
    
    The Fast Gradient Sign Method (FGSM) is a simple and fast adversarial attack
    that perturbs the input by epsilon in the direction of the gradient of the loss
    with respect to the input.
    
    Mathematical formulation:
    x_adv = x + epsilon * sign(gradient_x(J(theta, x, y)))
    
    Where:
    - x is the original input
    - epsilon is the perturbation magnitude
    - J is the loss function
    - theta are the model parameters
    - y is the true label
    """
    
    def __init__(self, model: nn.Module, device: str = 'cpu'):
        """
        Initialize the FGSM attack
        
        Args:
            model: The target neural network model
            device: Device to run computations on ('cpu' or 'cuda')
        """
        self.model = model
        self.device = device
        self.model.eval()
        self.model.to(device)
    
    def fgsm_attack(self, image: torch.Tensor, epsilon: float, data_grad: torch.Tensor) -> torch.Tensor:
        """
        Core FGSM attack function that generates the adversarial perturbation
        
        Args:
            image: Original input image tensor
            epsilon: Perturbation magnitude (attack strength)
            data_grad: Gradient of loss w.r.t. input image
            
        Returns:
            Adversarial image tensor
        """
        # Create the perturbation by taking the sign of the gradient
        perturbation = epsilon * data_grad.sign()
        
        # Apply the perturbation to the original image
        perturbed_image = image + perturbation
        
        # Clamp the perturbed image to maintain valid pixel range [0, 1]
        perturbed_image = torch.clamp(perturbed_image, 0, 1)
        
        return perturbed_image
    
    def generate(self, image: torch.Tensor, target: torch.Tensor, epsilon: float = 0.1) -> Tuple[torch.Tensor, bool]:
        """
        Generate adversarial example using FGSM
        
        Args:
            image: Input image tensor (normalized to [0, 1])
            target: True label tensor
            epsilon: Attack strength (default: 0.1)
            
        Returns:
            Tuple of (adversarial_image, attack_success)
        """
        # Ensure image requires gradient computation
        image = image.clone().detach().requires_grad_(True)
        image = image.to(self.device)
        target = target.to(self.device)
        
        # Forward pass through the model
        output = self.model(image)
        
        # Get the original prediction
        original_pred = output.argmax(dim=1).item()
        
        # Special case: if epsilon is 0, no attack should occur
        if epsilon == 0.0:
            return image.detach(), False
        
        # Calculate the loss (using negative log likelihood for classification)
        loss = F.nll_loss(output, target)
        
        # Zero all existing gradients
        self.model.zero_grad()
        
        # Backward pass to compute gradients
        loss.backward()
        
        # Get the gradient of the loss w.r.t. input image
        data_grad = image.grad.data
        
        # Generate the adversarial example
        perturbed_image = self.fgsm_attack(image, epsilon, data_grad)
        
        # Get prediction on adversarial example
        with torch.no_grad():
            adv_output = self.model(perturbed_image)
            adv_pred = adv_output.argmax(dim=1).item()
        
        # Attack is successful if prediction changes
        attack_success = (original_pred != adv_pred)
        
        return perturbed_image.detach(), attack_success
    
    def evaluate_robustness(self, test_loader, epsilon_values: list = None) -> dict:
        """
        Evaluate model robustness against FGSM attacks with different epsilon values
        
        Args:
            test_loader: DataLoader with test data
            epsilon_values: List of epsilon values to test
            
        Returns:
            Dictionary with evaluation results
        """
        if epsilon_values is None:
            epsilon_values = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
        
        results = {}
        
        for epsilon in epsilon_values:
            correct = 0
            total = 0
            
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                
                if epsilon == 0.0:
                    # Clean accuracy (no attack)
                    output = self.model(data)
                    pred = output.argmax(dim=1)
                    correct += pred.eq(target.view_as(pred)).sum().item()
                else:
                    # Attack each sample
                    for i in range(data.size(0)):
                        single_data = data[i:i+1]
                        single_target = target[i:i+1]
                        
                        perturbed_data, _ = self.generate(single_data, single_target, epsilon)
                        
                        with torch.no_grad():
                            output = self.model(perturbed_data)
                            pred = output.argmax(dim=1)
                            correct += pred.eq(single_target.view_as(pred)).sum().item()
                
                total += target.size(0)
            
            accuracy = 100. * correct / total
            results[f'epsilon_{epsilon}'] = {
                'accuracy': accuracy,
                'correct': correct,
                'total': total
            }
        
        return results


def load_mnist_model():
    """
    Simple CNN model for MNIST dataset
    """
    class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.conv1 = nn.Conv2d(1, 32, 3, 1)
            self.conv2 = nn.Conv2d(32, 64, 3, 1)
            self.dropout1 = nn.Dropout(0.25)
            self.dropout2 = nn.Dropout(0.5)
            self.fc1 = nn.Linear(9216, 128)
            self.fc2 = nn.Linear(128, 10)

        def forward(self, x):
            x = self.conv1(x)
            x = F.relu(x)
            x = self.conv2(x)
            x = F.relu(x)
            x = F.max_pool2d(x, 2)
            x = self.dropout1(x)
            x = torch.flatten(x, 1)
            x = self.fc1(x)
            x = F.relu(x)
            x = self.dropout2(x)
            x = self.fc2(x)
            output = F.log_softmax(x, dim=1)
            return output
    
    return Net()


if __name__ == "__main__":
    # Example usage and testing
    print("FGSM Implementation Test")
    
    # Create a simple model
    model = load_mnist_model()
    
    # Create attack instance
    attack = Attack(model)
    
    # Create dummy data for testing
    dummy_image = torch.randn(1, 1, 28, 28)
    dummy_target = torch.tensor([5])
    
    # Generate adversarial example
    adv_image, success = attack.generate(dummy_image, dummy_target, epsilon=0.1)
    
    print(f"Original image shape: {dummy_image.shape}")
    print(f"Adversarial image shape: {adv_image.shape}")
    print(f"Attack successful: {success}")
    print("FGSM implementation completed successfully!")
