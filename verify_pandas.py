import pandas as pd
print(f"Pandas version: {pd.__version__}")
try:
    df = pd.DataFrame({'a': [1, 2, 3]})
    csv = df.to_csv(index=False)
    print("Pandas CSV export successful")
except Exception as e:
    print(f"Error: {e}")
