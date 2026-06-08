"""
Ambulance Route Finder (full working script)
Requires: osmnx, networkx, folium, matplotlib
pip install osmnx networkx folium matplotlib
"""

import osmnx as ox
import networkx as nx
import folium
import math
import matplotlib.pyplot as plt
import sys


# --- Utilities ---
def haversine_m(lat1, lon1, lat2, lon2):
    """Return great-circle distance between two lat/lon points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def safe_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(0)

# --- Main ---
def main():
    print("🚑 Ambulance Route Finder (OSMnx + NetworkX)\n")
    # Central point near Connaught Place
    center_lat, center_lon = 28.6315, 77.2167
    # radius to fetch graph (meters)
    graph_radius_m = 2500

    print(f"📍 Fetching road network around Connaught Place (radius {graph_radius_m} m)...")
    try:
        G = ox.graph_from_point((center_lat, center_lon), dist=graph_radius_m, network_type="drive")
    except Exception as e:
        print("❌ Error fetching graph from OSM: ", e)
        print("Make sure you have internet and required packages installed.")
        return

    # user inputs
    print("\nEnter addresses/places near Connaught Place (or nearby New Delhi locations).")
    start_addr = safe_input("Start address (e.g. 'Rajiv Chowk Metro Station, New Delhi'): ").strip()
    end_addr = safe_input("Destination address (e.g. 'India Gate, New Delhi'): ").strip()

    if not start_addr or not end_addr:
        print("❌ Both start and destination are required.")
        return

    # geocode addresses to (lat, lon)
    try:
        start_point = ox.geocode(start_addr)   # returns (lat, lon)
        end_point = ox.geocode(end_addr)
    except Exception as e:
        print("❌ Geocoding failed:", e)
        print("Try a more specific address or check your internet connection.")
        return

    print(f"\nStart geocoded to: {start_point}")
    print(f"End geocoded to:   {end_point}")

    # find nearest graph nodes to these coordinates
    try:
        # OSMnx nearest_nodes expects (G, X, Y) where X=lon, Y=lat (older versions), or use distance.nearest_nodes
        # using ox.distance.nearest_nodes for compatibility
        start_node = ox.distance.nearest_nodes(G, X=start_point[1], Y=start_point[0])
        end_node = ox.distance.nearest_nodes(G, X=end_point[1], Y=end_point[0])
    except Exception:
        # fallback to the older signature if necessary
        start_node = ox.nearest_nodes(G, start_point[1], start_point[0])
        end_node = ox.nearest_nodes(G, end_point[1], end_point[0])

    # compute how far the geocoded point is from the matched node (warn if outside the fetched area)
    node_start_lat = G.nodes[start_node]["y"]
    node_start_lon = G.nodes[start_node]["x"]
    node_end_lat = G.nodes[end_node]["y"]
    node_end_lon = G.nodes[end_node]["x"]

    dist_start_to_node = haversine_m(start_point[0], start_point[1], node_start_lat, node_start_lon)
    dist_end_to_node = haversine_m(end_point[0], end_point[1], node_end_lat, node_end_lon)

    print(f"\nDistance from START address to matched road node: {int(dist_start_to_node)} m")
    print(f"Distance from DEST address to matched road node:  {int(dist_end_to_node)} m")

    # if the match is far from graph center, warn user and optionally continue
    max_allowed = graph_radius_m + 200  # if user typed something outside the fetch radius
    center_to_start = haversine_m(center_lat, center_lon, start_point[0], start_point[1])
    center_to_end = haversine_m(center_lat, center_lon, end_point[0], end_point[1])
    if center_to_start > graph_radius_m*1.2 or center_to_end > graph_radius_m*1.2:
        print("\n⚠️ Warning: One of the addresses appears to be outside the fetched map area.")
        print("You may get a long route or 'no path' if the nodes are disconnected.")
        # we continue anyway

    # compute shortest path
    try:
        route = nx.shortest_path(G, start_node, end_node, weight="length")
    except nx.NetworkXNoPath:
        print("\n❌ No path found between the selected locations within the road graph.")
        print("Try a different pair of addresses closer to each other or increase the graph radius.")
        return
    except Exception as e:
        print("\n❌ Error computing route:", e)
        return

    # route stats
    num_steps = len(route)
    total_length_m = nx.shortest_path_length(G, start_node, end_node, weight="length")
    total_length_km = total_length_m / 1000.0

    print("\n✅ Shortest Path Found!")
    print("➡ Number of steps (nodes):", num_steps)
    print(f"➡ Total distance (meters): {total_length_m:.1f} m  ({total_length_km:.3f} km)")
    print("➡ Route (first 12 node IDs):", route[:12], "..." if num_steps>12 else "")

    # prepare list of (lat, lon) for plotting
    route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

    # --- Save Folium interactive map ---
    try:
        m = folium.Map(location=route_coords[0], zoom_start=14)
        folium.PolyLine(route_coords, weight=7, opacity=0.8).add_to(m)
        folium.Marker(route_coords[0], popup="Start: " + start_addr, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(route_coords[-1], popup="End: " + end_addr, tooltip="End", icon=folium.Icon(color="red")).add_to(m)
        # add a popup with distance
        folium.map.Popup(f"Estimated driving distance: {total_length_m:.1f} m").add_to(m)
        folium.LayerControl().add_to(m)
        html_file = "route.html"
        m.save(html_file)
        print(f"\n🗺 Interactive map saved to: {html_file} (open in a browser)")
    except Exception as e:
        print("⚠️ Could not create folium map:", e)

    # --- Save Matplotlib plot (static) ---
    try:
        fig, ax = ox.plot_graph_route(G, route, show=False, close=False)
        # annotate distance on plot
        ax.set_title(f"Route: {start_addr} → {end_addr}\n{total_length_m:.1f} m ({total_length_km:.3f} km)")
        png_file = "route.png"
        fig.set_size_inches(10, 10)
        fig.savefig(png_file, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"🖼 Static image saved to: {png_file}")
    except Exception as e:
        print("⚠️ Could not create static route plot with matplotlib:", e)

    print("\nDone. Stay safe! 🚑")

if __name__ == "__main__":
    main()
