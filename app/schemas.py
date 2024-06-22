from typing import Optional
from pydantic import BaseModel
from enum import Enum
import numpy as np
from datetime import datetime


class AlertLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FXPrice(BaseModel):
    currency_pair: str
    price_series: np.array


class Alert(BaseModel):
    timestamp: datetime
    currency_pair: str
    alert_level: AlertLevel
    message: Optional[str]

    class Config:
        orm_mode = True
