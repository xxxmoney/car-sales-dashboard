from src.data_loader import DataLoader

# TODO: run this whole thing


# TODO: just here for testing now, remove later
loader = DataLoader()

data = loader.load_data()

print(f"Data loaded: {len(data)} rows")
print(f"Columns: {data.columns.tolist()}")
