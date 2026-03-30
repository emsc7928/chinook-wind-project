# Chinook Wind Events and Wind Energy Potential Along the Colorado Front Range

## Overview

This project analyzes the frequency of westerly wind events and strong Chinook events near Boulder, Colorado, and evaluates their impact on wind energy potential. The analysis uses multi-year wind data (2007–2014) from the NREL Wind Toolkit.

## Research Question

How frequently do westerly wind events and Chinook events occur along the Colorado Front Range, and how do these events influence wind power production?

## Data

Wind data were obtained using the NREL Wind Toolkit API at a location near Boulder, Colorado (40.0150°N, -105.2705°W). The dataset includes hourly wind speed and wind direction at 100 m above ground level.

## Methods

Westerly wind events were defined as periods with:

* Wind direction between 250° and 290°
* Wind speed ≥ 8 m/s
* Duration of at least 2 consecutive hours

Chinook events were defined as a subset of westerly wind events with:

* Wind speed ≥ 17.88 m/s

Wind energy potential was estimated using a relative power proxy proportional to the cube of wind speed (U³).

## Results

* Westerly wind events occurred during **5,240 hours** (~7.48% of total observations).
* Chinook events occurred during **819 hours** (~1.17% of total observations).
* A total of **1,162 westerly wind events** were identified.
* Most Chinook events occurred within the turbine operating range, but **195 hours exceeded cut-out thresholds (>25 m/s)**.
* Chinook events represent rare but high-impact periods for wind energy production.

## Repository Structure

chinook-wind-project/
├── scripts/
│   └── chinook_analysis.py
├── figures/
├── README.md
└── requirements.txt

## Requirements

* pandas
* matplotlib
* requests

## How to Run

1. Insert your NREL API key into the script:
   API_KEY = "YOUR_API_KEY_HERE"
2. Run the script:
   python scripts/chinook_analysis.py
3. Figures will be saved in the `figures/` folder.

## Author

Emery Schattinger
University of Colorado Boulder
