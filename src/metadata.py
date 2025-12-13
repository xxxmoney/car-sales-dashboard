from dataclasses import dataclass


@dataclass
class Metadata:
    min_year: int
    max_year: int
    average_price: float
    min_price: int
    max_price: int
    min_mileage: int
    max_mileage: int
