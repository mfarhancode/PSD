import pandas as pd

df_co = pd.read_csv("Pollutant_CO_Sialkot.csv")
df_no2 = pd.read_csv("Pollutant_NO2_Sialkot.csv")
df_o3 = pd.read_csv("Pollutant_O3_Sialkot.csv")
df_so2 = pd.read_csv("Pollutant_SO2_Sialkot.csv")

# Drop feature_index column from each file
for df in [df_co, df_no2, df_o3, df_so2]:
    if "feature_index" in df.columns:
        df.drop(columns=["feature_index"], inplace=True)

# Merge on date
merged = df_co.merge(df_no2, on="date", how="outer") \
              .merge(df_o3, on="date", how="outer") \
              .merge(df_so2, on="date", how="outer")

# Standardize column names to lowercase (PostgreSQL handles lowercase best)
merged.columns = [c.strip().lower() for c in merged.columns]

# Sort by date and save
merged.sort_values("date").reset_index(drop=True, inplace=True)
merged.to_csv("AirQualitySialkot.csv", index=False)
print("Merged file saved successfully! Shape:", merged.shape)