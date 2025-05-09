import os
import json
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18
from PIL import Image
from tkinter import ttk, messagebox
# Load a pre-trained ResNet18 model
class FeatureExtractor(nn.Module):
    def __init__(self):
        super(FeatureExtractor, self).__init__()
        model = resnet18(pretrained=True)
        self.feature_extractor = nn.Sequential(*list(model.children())[:-1])  # Remove the classification layer

    def forward(self, x):
        features = self.feature_extractor(x)
        return features.view(features.size(0), -1)  # Flatten the output

# Initialize the feature extractor
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = FeatureExtractor().to(device)
model.eval()

# Image transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to match ResNet input
    transforms.ToTensor(),          # Convert to tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
])

def extract_features(image_path):
    """Extract feature vector from an image."""
    image = Image.open(image_path).convert("RGB")  # Ensure 3 channels
    image = transform(image).unsqueeze(0).to(device)  # Add batch dimension
    with torch.no_grad():
        features = model(image)
    return features.cpu()

def cosine_similarity(feature1, feature2):
    """Compute cosine similarity between two feature vectors."""
    return torch.nn.functional.cosine_similarity(feature1, feature2).item()

def match_already_exists(img1_path, folder_path='../data/gestures/'):
    """Find the most similar gesture using cosine similarity."""
    img1_features = extract_features(img1_path)  # Extract features of the input image

    best_match = None
    best_similarity = 0.9  # Initialize with the lowest similarity value

    for filename in os.listdir(folder_path):
        # Create the full path for the image
        img2_path = os.path.join(folder_path, filename)

        # Only process files with image extensions
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            img2_features = extract_features(img2_path)  # Extract features of the stored image
            similarity = cosine_similarity(img1_features, img2_features)

            # Track the best match (highest similarity)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = img2_path
            #print(f"Comparing {img1_path} with {img2_path}... Similarity: {similarity}")

    if best_match:
        print(f"The best matching gesture is: {best_match} with Similarity: {best_similarity}")
        filename = os.path.splitext(os.path.basename(best_match))[0]
        app_data = {}
        with open('../data/app_data.json', 'r') as apps:
            app_data = json.load(apps)
        return app_data[filename]['command']
    else:
        print("No similar gestures found.")
        messagebox.showinfo("Gesture error","Gesture not found!")
        return None

# Example usage


