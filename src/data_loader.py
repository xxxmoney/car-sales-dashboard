import pandas as pd
from src import constants


class DataLoader:
    """ Handles loading and cleaning of data """

    def __init__(self, filepath: str = constants.DATA_SET_PATH):
        self.filepath = filepath
        self.data = None

    def load_data(self) -> pd.DataFrame:
        """ Load CSV and perform comprehensive cleaning """
        # Load raw data
        self.data = pd.read_csv(self.filepath)

        # 1. Drop rows with missing critical values
        # We need these columns to be valid for our charts to work correctly
        # 'make', 'model', 'fuel' -> needed for Sunburst hierarchy
        # 'hp', 'gear' -> needed for filters and scatter plots
        critical_columns = ["make", "model", "fuel", "hp", "gear"]
        self.data.dropna(subset=critical_columns, inplace=True)

        # 2. Convert types
        # Cast year to integer
        self.data["year"] = self.data["year"].astype(int)

        # 3. Handle outliers/invalid data
        # E.g., remove cars with 0 HP or suspicious low price
        self.data = self.data[self.data["price"] > 100]
        self.data = self.data[self.data["hp"] > 0]

        return self.data

    def get_brands(self):
        """ Return sorted list of unique car brands """
        if self.data is None:
            self.load_data()
        return sorted(self.data["make"].unique())

    def get_year_range(self):
        """ Return min and max production year """
        if self.data is None:
            self.load_data()
        return self.data["year"].min(), self.data["year"].max()