from __future__ import annotations

import torch
from torch import nn


class HybridFusionModel(nn.Module):
    def __init__(
        self,
        dynamic_features: int = 1,
        static_features: int = 2,
        hidden_size: int = 64,
    ) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=dynamic_features,
            hidden_size=hidden_size,
            num_layers=2,
            batch_first=True,
            dropout=0.1,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_size + static_features + 1, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(
        self,
        dynamic: torch.Tensor,
        lgb_prediction: torch.Tensor,
        static: torch.Tensor,
    ) -> torch.Tensor:
        _, (hidden, _) = self.lstm(dynamic)
        fused = torch.cat((hidden[-1], lgb_prediction, static), dim=1)
        return self.head(fused).squeeze(1)