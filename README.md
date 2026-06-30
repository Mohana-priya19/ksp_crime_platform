markdown# KSP Crime Intelligence Platform

AI-driven crime analytics and visualization platform built for the **Karnataka State Police Datathon 2026 — Challenge 2**.

## Overview

This platform helps law enforcement identify repeat offenders who use multiple fake identities across different districts, visualize crime hotspots, and explore district-level crime statistics — all from a single, real-time dashboard.

## Features

- **Crime Dashboard** — live statistics across all Karnataka districts, crime type distribution, and top-district rankings
- **Suspect Identity Deduplication** — AI engine using Soundex phonetic matching, fuzzy name comparison, and Union-Find clustering to detect when the same criminal has filed FIRs under multiple fake names
- **Suspect Profile Pages** — full investigative profile for each detected identity cluster, including all known aliases, FIR history, and crime breakdown
- **Crime Hotspot Map** — interactive Folium heatmap with crime-type filtering
- **Cross-District Network Graph** — D3.js force-directed graph visualizing how suspect clusters operate across district boundaries
- **District Drilldown** — per-district crime statistics and breakdowns

## Tech Stack

- **Backend**: Python, Flask
- **Data**: Pandas, synthetic FIR dataset generator (5,000+ records)
- **Dedup Engine**: Soundex + SequenceMatcher + Union-Find clustering
- **Frontend**: HTML, CSS, Plotly.js, D3.js, Folium

## Project Structure
ksp_crime_platform/
├── app/
│   ├── app.py              # Flask application & routes
│   ├── static/
│   │   └── theme.css       # Shared design system
│   └── templates/
│       ├── index.html      # Dashboard
│       ├── dedup.html      # Identity deduplication
│       ├── suspect.html    # Suspect profile page
│       ├── network.html    # Cross-district network graph
│       ├── district.html   # District drilldown
│       └── map.html        # Hotspot map
├── engines/
│   ├── data_generator.py   # Synthetic FIR data generator
│   ├── dedup_engine.py     # Identity deduplication engine
│   └── hotspot_map.py      # Folium heatmap generator
└── data/
└── karnataka_fir_synthetic.csv

## Running Locally

```bash
cd ksp_crime_platform
python app/app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Team

Built by a team of 4 for the KSP Datathon 2026, Challenge 2.

## Deployment

Target deployment platform: **Zoho Catalyst**
