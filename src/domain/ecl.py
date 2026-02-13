from dataclasses import dataclass
from datetime import date


@dataclass
class ECL:
    value: float
    stage: str
    calculation_date: date
    scenario: str
    model_version: str
