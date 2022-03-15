import pandas as pd
import geopandas as gpd
import folium
import json
import rtree
from folium import plugins


def crimeMap(crimeData, geoData):
    """
    The function crimeMap takes in the crime dataset and the geo dataset.
    Clean and join two datasets.
    Plot the shapes of all MCPP areas in city of Seattle where each area is
    colored according to crime cases with a legend. Hovering over each area
    will show the name and number of crime cases for that area.
    """
    df = pd.read_csv(crimeData).dropna()
    mcpp = gpd.read_file(geoData)
    # Load Data
    mcpp.loc[mcpp.NAME == "DOWNTOWN COMMERICAL",
             "NAME"] = "DOWNTOWN COMMERCIAL"
    mcpp.loc[mcpp.NAME == "INTERNATIONAL DISTRICT - EAST",
             "NAME"] = "CHINATOWN/INTERNATIONAL DISTRICT"
    mcpp.loc[mcpp.NAME == "INTERNATIONAL DISTRICT - WEST",
             "NAME"] = "CHINATOWN/INTERNATIONAL DISTRICT"
    mcpp.loc[mcpp.NAME == "NORTH CAPITOL HILL", "NAME"] = "CAPITOL HILL"
    mcpp.loc[mcpp.NAME == "JUDKINS PARK",
             "NAME"] = "JUDKINS PARK/NORTH BEACON HILL"
    mcpp.loc[mcpp.NAME == "MT BAKER/NORTH RAINIER", "NAME"] = "MOUNT BAKER"
    mcpp.loc[mcpp.NAME == "NORTH BEACON/JEFFERSON PARK",
             "NAME"] = "NORTH BEACON HILL"
    mcpp.loc[mcpp.NAME == "COMMERCIAL DUWAMISH", "NAME"] = "NORTH DELRIDGE"
    # Clean Data
    dis = df.groupby('MCPP', as_index=False).size()
    merged_df = dis.merge(mcpp, left_on='MCPP',
                          right_on='NAME', how='outer').dropna()
    merged_df.rename({'size': 'Incidents'}, axis=1, inplace=True)
    merged_df = gpd.GeoDataFrame(merged_df)
    # Merge and groupby the data by the name of
    # each area.
    seaMap = folium.Map([47.6062, -122.3321], zoom_start=9)
    # Create map
    folium.TileLayer('CartoDB positron', name="Light Map",
                     control=False).add_to(seaMap)
    choropleth = folium.Choropleth(
        geo_data=merged_df,
        fill_opacity=0.5,
        line_weight=1.5,
        data=merged_df,
        columns=['MCPP', 'Incidents'],
        key_on='feature.properties.MCPP',
        highlight=True,
        fill_color='YlOrRd',
        nan_fill_opacity=0,
        name='Incidents',
    ).add_to(seaMap)
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['MCPP', 'Incidents'], labels=True)
    )
    # Add hovering feature to the map.
    return seaMap
