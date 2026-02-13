from dataclasses import dataclass


@dataclass
class Loan:
    loan_id: str
    type: str
    exposure: float
