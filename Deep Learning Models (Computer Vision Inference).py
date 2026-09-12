import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

class LungCancerDetector(nn.Module):
    def __init__(self):
        super(LungCancerDetector, self).__init__()
        # DenseNet or ResNet backbone configuration for medical imaging feature extraction
        self.backbone = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
        self.backbone.classifier = nn.Sequential(
            nn.Linear(self.backbone.classifier.in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, 2),  # Binary classification: [Normal/Benign, Anomalous/Malignant]
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        return self.backbone(x)

def run_inference(image_path: str):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LungCancerDetector().to(device)
    model.eval()

    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path).convert("RGB")
    tensor = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(tensor)
        probabilities = output[0].cpu().numpy()
    
    malignancy_prob = float(probabilities[1])
    return {
        "malignancy_probability": round(malignancy_prob, 4),
        "anomaly_detected": malignancy_prob > 0.50
    }