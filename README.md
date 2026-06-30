# KSP Crime Intelligence Platform

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
