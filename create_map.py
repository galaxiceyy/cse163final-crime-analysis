import pandas as pd
import gmplot
import geopandas as gpd
import folium
import json
import rtree
from folium import plugins

def crimeMap(crimeData, geoData):
    zip_df = pd.read_csv(crimeData).dropna()
    mcpp = gpd.read_file(geoData)
    mcpp.loc[mcpp.NAME == "DOWNTOWN COMMERICAL", "NAME"] = "DOWNTOWN COMMERCIAL"
    mcpp.loc[mcpp.NAME == "INTERNATIONAL DISTRICT - EAST", "NAME"] = "CHINATOWN/INTERNATIONAL DISTRICT"
    mcpp.loc[mcpp.NAME == "INTERNATIONAL DISTRICT - WEST", "NAME"] = "CHINATOWN/INTERNATIONAL DISTRICT"
    mcpp.loc[mcpp.NAME == "NORTH CAPITOL HILL", "NAME"] = "CAPITOL HILL"
    mcpp.loc[mcpp.NAME == "JUDKINS PARK", "NAME"] = "JUDKINS PARK/NORTH BEACON HILL"
    mcpp.loc[mcpp.NAME == "MT BAKER/NORTH RAINIER", "NAME"] = "MOUNT BAKER"
    mcpp.loc[mcpp.NAME == "NORTH BEACON/JEFFERSON PARK", "NAME"] = "NORTH BEACON HILL"
    mcpp.loc[mcpp.NAME == "COMMERCIAL DUWAMISH", "NAME"] = "NORTH DELRIDGE"
    dis = zip_df.groupby('MCPP', as_index = False).size()
    merged_df = dis.merge(mcpp, left_on='MCPP',
                          right_on='NAME', how='outer').dropna()
    merged_df.rename({'size': 'Incidents'}, axis=1, inplace=True)
    merged_df = gpd.GeoDataFrame(merged_df)
    seaMap = folium.Map([47.6062,-122.3321], zoom_start=9)
    folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(seaMap)
    choropleth = folium.Choropleth(
        geo_data= merged_df,
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
    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['MCPP', 'Incidents'], labels = True))
    return seaMap
