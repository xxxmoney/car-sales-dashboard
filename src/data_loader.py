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
        """ Return sorted list of unique car brands """
        if self.data is None:
            self.load_data()
        return sorted(self.data["make"].unique())

    def get_year_range(self):
        """ Return min and max production year """
        if self.data is None:
            self.load_data()
        return self.data["year"].min(), self.data["year"].max()