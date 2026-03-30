import pandas as pd
import requests
from io import StringIO
import matplotlib.pyplot as plt
import os

# =========================
# 0. SET WORKING DIRECTORY + CREATE FOLDERS
# =========================
project_path = r"C:/Users/Emery Schattinger/Downloads/chinook-wind-project"
os.chdir(project_path)

os.makedirs("figures", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

# =========================
# 1. SETTINGS
# =========================
API_KEY = "uPq76u4GK0kzqFeRuqUQvxhao3AzofbMDXrk6xPC"
EMAIL = "emsc7928@colorado.edu"

YEARS = list(range(2007, 2015))

DIR_MIN = 250
DIR_MAX = 290
WESTERLY_SPEED_THRESHOLD = 8.0
MIN_DURATION_HOURS = 2
CHINOOK_EVENT_THRESHOLD = 17.88

# =========================
# 2. DOWNLOAD + COMBINE DATA
# =========================
all_dfs = []

for year in YEARS:
    params = {
        "api_key": API_KEY,
        "email": EMAIL,
        "wkt": "POINT(-105.2705 40.0150)",
        "names": str(year),
        "attributes": "windspeed_100m,winddirection_100m",
        "interval": "60"
    }

    url = "https://developer.nrel.gov/api/wind-toolkit/v2/wind/wtk-download.csv"
    response = requests.get(url, params=params)

    print(f"Year {year}: status = {response.status_code}")

    df_year = pd.read_csv(StringIO(response.text), skiprows=1)
    all_dfs.append(df_year)

df = pd.concat(all_dfs, ignore_index=True)

# =========================
# 3. CLEAN DATA
# =========================
df["datetime"] = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])

df = df.rename(columns={
    "wind speed at 100m (m/s)": "wind_speed",
    "wind direction at 100m (deg)": "wind_dir"
})

df = df[["datetime", "wind_speed", "wind_dir"]].dropna()
df = df.sort_values("datetime").reset_index(drop=True)

df["year"] = df["datetime"].dt.year
df["month"] = df["datetime"].dt.month

# =========================
# 4. DEFINE EVENTS
# =========================
df["westerly_like"] = (
    (df["wind_dir"] >= DIR_MIN) &
    (df["wind_dir"] <= DIR_MAX) &
    (df["wind_speed"] >= WESTERLY_SPEED_THRESHOLD)
)

df["run_id"] = (df["westerly_like"] != df["westerly_like"].shift()).cumsum()
df["run_length"] = df.groupby("run_id")["westerly_like"].transform("size")

df["westerly_event_hour"] = df["westerly_like"] & (df["run_length"] >= MIN_DURATION_HOURS)

df["event_start"] = (
    df["westerly_event_hour"] &
    (~df["westerly_event_hour"].shift(fill_value=False))
)

df["chinook_event"] = (
    df["westerly_event_hour"] &
    (df["wind_speed"] >= CHINOOK_EVENT_THRESHOLD)
)

# =========================
# 5. LABELS + POWER
# =========================
df["plot_category"] = "Non-Westerly"
df.loc[df["westerly_event_hour"], "plot_category"] = "Westerly Wind"
df.loc[df["chinook_event"], "plot_category"] = "Chinook Event"

df["turbine_range"] = "Operating range"
df.loc[df["wind_speed"] < 5, "turbine_range"] = "Below operating range"
df.loc[df["wind_speed"] > 25, "turbine_range"] = "Above cut-out range"

df["relative_power"] = df["wind_speed"] ** 3

# =========================
# 6. SUMMARY
# =========================
total_obs = len(df)

westerly_hours = int(df["westerly_event_hour"].sum())
chinook_hours = int(df["chinook_event"].sum())

print("\n===== SUMMARY =====")
print("Total observations:", total_obs)
print("Westerly wind hours:", westerly_hours)
print("Chinook event hours:", chinook_hours)
print("Chinook frequency:", round((chinook_hours / total_obs) * 100, 2), "%")
print("Total events:", int(df["event_start"].sum()))

print("\nChinook turbine ranges:")
print(df.loc[df["chinook_event"], "turbine_range"].value_counts())

# =========================
# 7. FIGURE 1
# =========================
events_per_year = df.loc[df["event_start"]].groupby("year").size()

plt.figure(figsize=(10,5))
events_per_year.plot(kind='bar')
plt.ylabel("Number of Events")
plt.title("Annual Westerly Wind Event Frequency (2007–2014)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
#plt.savefig("figures/figure1_events_per_year.png", dpi=300)
plt.show()

# =========================
# 8. FIGURE 2
# =========================
non_ws = df[df["plot_category"] == "Non-Westerly"]["wind_speed"]
west_ws = df[df["plot_category"] == "Westerly Wind"]["wind_speed"]
chinook_ws = df[df["plot_category"] == "Chinook Event"]["wind_speed"]

plt.figure(figsize=(8,5))
plt.boxplot([non_ws, west_ws, chinook_ws],
            labels=["Non-Westerly", "Westerly Wind", "Chinook Event"])
plt.ylabel("Wind Speed (m/s)")
plt.title("Wind Speed Distribution")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
#plt.savefig("figures/figure2_wind_speed.png", dpi=300)
plt.show()

# =========================
# 9. FIGURE 3
# =========================
non_p = df[df["plot_category"] == "Non-Westerly"]["relative_power"]
west_p = df[df["plot_category"] == "Westerly Wind"]["relative_power"]
chinook_p = df[df["plot_category"] == "Chinook Event"]["relative_power"]

plt.figure(figsize=(8,5))
plt.boxplot([non_p, west_p, chinook_p],
            labels=["Non-Westerly", "Westerly Wind", "Chinook Event"])
plt.yscale("log")
plt.ylabel("Relative Power (U³, log scale)")
plt.title("Relative Wind Power Distribution")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
#plt.savefig("figures/figure3_power.png", dpi=300)
plt.show()