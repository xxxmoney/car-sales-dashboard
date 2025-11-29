import pandas as pd
from src import constants

class DataLoader:
    """ Handles loading and cleaning of data """

    def __init__(self, filepath: str = constants.DATA_SET_PATH):
        self.filepath = filepath
        self.data = None

    def load_data(self) -> pd.DataFrame:
        """ Load CSV and perform basic cleaning """
        # Load raw data
        self.data = pd.read_csv(self.filepath)

        # Drop rows with missing critical values
        # HP and Gear are critical for our analysis
        self.data.dropna(subset=["hp", "gear"], inplace=True)

        # Cast year to integer
        self.data["year"] = self.data["year"].astype(int)

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