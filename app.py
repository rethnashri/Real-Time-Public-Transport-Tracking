import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Coimbatore Bus Tracker",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Real-Time Public Transport Tracking")
st.subheader("Coimbatore City — Transport Dashboard")

st.info(
    "DEMO MODE: Bus locations and passenger counts are simulated, "
    "not actual live GPS data."
)

# Sample bus information
data = {
    "Bus": ["BUS-01", "BUS-02", "BUS-03", "BUS-04", "BUS-05", "BUS-06"],
    "Route": ["Route A", "Route A", "Route B", "Route B", "Route C", "Route C"],
    "Status": ["Active", "Active", "Delayed", "Active", "Inactive", "Active"],
    "Delay_Minutes": [2, 5, 12, 3, 0, 8],
    "Passengers": [35, 42, 28, 38, 0, 31]
}

df = pd.DataFrame(data)

# Coimbatore demo coordinates
# These are illustrative points, not verified bus routes.
routes = {
    "Route A": [
        (11.0168, 76.9558),
        (11.0200, 76.9600),
        (11.0240, 76.9650),
        (11.0280, 76.9700),
        (11.0320, 76.9750)
    ],
    "Route B": [
        (11.0050, 76.9600),
        (11.0090, 76.9650),
        (11.0130, 76.9700),
        (11.0170, 76.9750),
        (11.0210, 76.9800)
    ],
    "Route C": [
        (11.0300, 76.9400),
        (11.0260, 76.9450),
        (11.0220, 76.9500),
        (11.0180, 76.9550),
        (11.0140, 76.9600)
    ]
}

# Calculate dashboard values
total_buses = len(df)
active_buses = (df["Status"] == "Active").sum()
total_routes = df["Route"].nunique()

running_buses = df[df["Status"] != "Inactive"]
average_delay = running_buses["Delay_Minutes"].mean()

# Summary cards
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Buses", total_buses)
c2.metric("Active Buses", active_buses)
c3.metric("Total Routes", total_routes)
c4.metric("Average Delay", f"{average_delay:.1f} min")

st.divider()

# Route filter
selected_route = st.selectbox(
    "Filter by route",
    ["All Routes"] + sorted(df["Route"].unique().tolist())
)

if selected_route == "All Routes":
    filtered_df = df.copy()
else:
    filtered_df = df[df["Route"] == selected_route].copy()

# Map
st.subheader("📍 Coimbatore Bus Map")
st.caption("Bus markers move in this demo every 5 seconds.")

bus_map = folium.Map(
    location=[11.0168, 76.9558],
    zoom_start=13
)

for _, bus in filtered_df.iterrows():
    route_points = routes[bus["Route"]]

    # Each refresh moves the simulated bus marker
    position_index = (
    int(bus["Bus"].split("-")[1]) - 1
) % len(route_points)
    current_position = route_points[position_index]

    # Draw the illustrative route
    folium.PolyLine(
        route_points,
        tooltip=bus["Route"],
        weight=4
    ).add_to(bus_map)

    # Show active bus markers
    if bus["Status"] != "Inactive":
        popup_text = (
            f'{bus["Bus"]}<br>'
            f'Route: {bus["Route"]}<br>'
            f'Status: {bus["Status"]}<br>'
            f'Passengers: {bus["Passengers"]}'
        )

        folium.Marker(
            location=current_position,
            tooltip=bus["Bus"],
            popup=popup_text,
            icon=folium.Icon(
                color="red" if bus["Status"] == "Delayed" else "green",
                icon="bus",
                prefix="fa"
            )
        ).add_to(bus_map)

st_folium(
    bus_map,
    width=None,
    height=450,
    use_container_width=True,
    key="coimbatore_map"
)

st.divider()

# Charts
left, right = st.columns(2)

with left:
    st.subheader("🚌 Buses by Route")

    route_counts = filtered_df.groupby("Route")["Bus"].count().reset_index()

    fig1 = px.bar(
        route_counts,
        x="Route",
        y="Bus",
        text="Bus",
        title="Number of Buses"
    )

    fig1.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("🚦 Bus Status")

    status_counts = filtered_df["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    fig2 = px.pie(
        status_counts,
        names="Status",
        values="Count",
        title="Bus Status Distribution"
    )

    fig2.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig2, use_container_width=True)

# Smaller passenger chart
st.subheader("👥 Passenger Count by Route")

passenger_data = (
    filtered_df.groupby("Route")["Passengers"].sum().reset_index()
)

fig3 = px.bar(
    passenger_data,
    x="Route",
    y="Passengers",
    text="Passengers",
    title="Passengers per Route"
)

fig3.update_layout(
    height=280,
    margin=dict(l=10, r=10, t=50, b=10)
)

st.plotly_chart(fig3, use_container_width=True)

# Bus details
st.subheader("📋 Bus Details")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Project prototype: Map positions, routes, passenger counts, "
    "and bus movement are illustrative demo data."
)