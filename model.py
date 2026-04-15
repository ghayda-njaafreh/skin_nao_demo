import torch
import torch.nn as nn


class SkinCNN(nn.Module):
    def __init__(self, num_classes: int = 7):
        super().__init__()

        # Feature extractor
        self.features = nn.Sequential(
            # Block 1: 3 -> 32
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),      # 28x28 -> 14x14
            nn.BatchNorm2d(32),

            # Block 2: 32 -> 64 -> 64
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),      # 14x14 -> 7x7
            nn.BatchNorm2d(64),

            # Block 3: 64 -> 128 -> 128
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),      # 7x7 -> 3x3
            nn.BatchNorm2d(128),

            # Block 4: 128 -> 256 -> 256
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)       # 3x3 -> 1x1
        )

        # Classifier: 5 FC layers with BatchNorm + Dropout at input
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.2),

            # 256*1*1 -> 256
            nn.Linear(256 * 1 * 1, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),

            # 256 -> 128
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),

            # 128 -> 64
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),

            # 64 -> 32
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32),

            # 32 -> num_classes
            nn.Linear(32, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.classifier(x)
        return x


def load_model(
    weights_path: str = "model.pth",
    device: str | None = None
) -> tuple[nn.Module, torch.device]:
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device)

    model = SkinCNN(num_classes=7)
    state_dict = torch.load(weights_path, map_location=device)
    model.load_state_dict(state_dict)

    model.to(device)
    model.eval()

    return model, device