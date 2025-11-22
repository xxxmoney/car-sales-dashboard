import pandas as pd

from src import constants


class DataLoader:
    """ Handles loading and basic cleaning of the cars dataset """

    def __init__(self, filepath: str = constants.DATA_SET_PATH):
        self.filepath = filepath
        self.df = None

    def load_data(self) -> pd.DataFrame:
        """Loads CSV and performs initial cleaning."""
        # Load data
        self.df = pd.read_csv(self.filepath)

        # Basic cleanup based on dataset info analysis
        # Drop rows where critical info is missing or doesn't make sense for analysis

        # Exclude NaNs from Horse Power
        self.df.dropna(subset=['hp'], inplace=True)
        # Exclude NaNs from Gear
        self.df.dropna(subset=['gear'], inplace=True)
        # Note - other columns don't have NaNs, so just exclude them only from these specified

        # Filter out extreme price outliers
        # Keep reasonable range e.g., 500 EUR to 500k EUR
        self.df = self.df[(self.df['price'] > 500) & (self.df['price'] < 500000)]

        # Convert year to int (sometimes read as float)
        self.df['year'] = self.df['year'].astype(int)

        return self.df

    def get_brands(self):
        """ Returns sorted list of unique car brands """
        if self.df is None:
            self.load_data()
        return sorted(self.df['make'].unique())

    def get_year_range(self):
        """ Returns min and max year """
        if self.df is None:
            self.load_data()
        return self.df['year'].min(), self.df['year'].max()

