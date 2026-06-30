import folium
from folium.plugins import HeatMap

def generate_map_html(df):
    # Center map on Karnataka
    m = folium.Map(location=[14.5, 75.9], zoom_start=7,
                   tiles='CartoDB positron')

    # Add heatmap
    heat_data = df[['latitude', 'longitude']].dropna().values.tolist()
    if heat_data:
        HeatMap(heat_data, radius=15, blur=10, min_opacity=0.4).add_to(m)

    # Add circle markers for each district center
    district_counts = df.groupby('district').size().reset_index(name='count')
    district_coords = df.groupby('district')[['latitude','longitude']].mean()

    for _, row in district_counts.iterrows():
        district = row['district']
        count = row['count']
        if district in district_coords.index:
            lat = district_coords.loc[district, 'latitude']
            lng = district_coords.loc[district, 'longitude']
            folium.CircleMarker(
                location=[lat, lng],
                radius=max(8, min(30, count / 10)),
                color='#1e3a5f',
                fill=True,
                fill_color='#2563eb',
                fill_opacity=0.6,
                popup=folium.Popup(f"<b>{district}</b><br>{count} FIRs", max_width=200),
                tooltip=f"{district}: {count} FIRs"
            ).add_to(m)

    return m._repr_html_()