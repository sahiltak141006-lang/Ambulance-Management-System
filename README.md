# 🚑 Ambulance Route Finder (Geospatial Optimization)

A production-grade Python optimization script that fetches real-world urban maps, matches address query string profiles to physical geographic coordinates, and calculates optimized navigation geometry routing configurations for emergency vehicles.

## Key Technical Workflows
* **Live GIS Grid Fetching:** Leverages `osmnx` to download and map localized driving transportation networks directly using OpenStreetMap data topologies.
* **Geocoding Pipelines:** Converts user string input locations ("Rajiv Chowk Metro Station") into float spatial latitude/longitude array pairs.
* **Geodesic Mathematical Safeguards:** Implements a custom mathematical Haversine metric tracking node-to-coordinate errors to warn operators if parameters fall outside of bounds.
* **Interactive HTML Maps:** Compiles calculations dynamically using `folium`, generating interactive leaf layer map interfaces featuring customized marker tags and route overlays.

## Tech Stack & Engine Dependency
* **Core Languages & Libraries:** Python, NetworkX, OSMnx, Folium, Matplotlib
* **Core Concepts:** Graph Traversal Optimization, Computational Geospatial Analysis, Mathematical Rerouting

## How to Set Up and Run Globally
1. Install project environment package dependencies:
```bash
pip install osmnx networkx folium matplotlib
