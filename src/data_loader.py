import math

import pandas as pd
from src import constants
from src.metadata import Metadata


class DataLoader:
    """ Handles loading and cleaning of data """

    def __init__(self, filepath: str = constants.DATA_SET_PATH):
        self.filepath = filepath
        self.data = None

    def load_data(self) -> pd.DataFrame:
        """ Loads CSV and perform comprehensive cleaning """

        # Load raw data
        self.data = pd.read_csv(self.filepath)

        # Drop invalid
        critical_columns = ["make", "model", "fuel", "hp", "gear"]
        self.data.dropna(subset=critical_columns, inplace=True)

        # Convert types
        self.data["year"] = self.data["year"].astype(int)

        # Handle outliers/invalid data
        self.data = self.data[self.data["price"] > 100]
        self.data = self.data[self.data["hp"] > 0]

        return self.data

    def get_brands(self):
        """ Returns sorted list of unique car brands """
        if self.data is None:
            self.load_data()
        return sorted(self.data["make"].unique())

    def get_year_range(self):
        """ Returns min and max production year """
        if self.data is None:
            self.load_data()
        return self.data["year"].min(), self.data["year"].max()

    def get_metadata(self) -> Metadata:
        min_year, max_year = self.get_year_range()

        return Metadata(
            min_year=min_year,
            max_year=max_year,
            average_price=self.data["price"].mean(),
            min_price=math.floor(self.data["price"].min()),
            max_price=math.ceil(self.data["price"].quantile(0.98)),
            min_mileage=math.floor(self.data["mileage"].min()),
            max_mileage=math.ceil(self.data["mileage"].quantile(0.98)),
        )