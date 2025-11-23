import pandas as pd
from src import constants


class DataLoader:
    """ Handles loading and basic cleaning of the cars dataset """

    def __init__(self, filepath: str = constants.DATA_SET_PATH):
        self.filepath = filepath
        self.data = None

    def load_data(self) -> pd.DataFrame:
        """ Loads CSV and performs initial cleaning """
        # Load data
        self.data = pd.read_csv(self.filepath)

        # Basic cleanup based on dataset info analysis
        # Drop rows where critical info is missing or doesn"t make sense for analysis

        # Exclude NaNs from Horse Power
        self.data.dropna(subset=["hp"], inplace=True)
        # Exclude NaNs from Gear
        self.data.dropna(subset=["gear"], inplace=True)
        # Note - other columns don"t have NaNs, so just exclude them only from these specified

        # Convert year to int (sometimes read as float)
        self.data["year"] = self.data["year"].astype(int)

        return self.data

    def get_brands(self):
        """ Returns sorted list of unique car brands """
        if self.data is None:
            self.load_data()
        return sorted(self.data["make"].unique())

    def get_year_range(self):
        """ Returns min and max year """
        if self.data is None:
            self.load_data()
        return self.data["year"].min(), self.data["year"].max()

