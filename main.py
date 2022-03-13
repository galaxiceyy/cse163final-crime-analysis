import pandas as pd
import geopy

def preprocess_crime_data(SPD_file_name):
    """
    Load in csv file. covert the offense start datatime into column
    filter the crime incidents occurred between 2018-2022.
    add zip code column from long/lat coordinates
    """
    df = pd.read_csv(SPD_file_name, usecols=["Report Number", "Offense Start DateTime", "Report DateTime", "Offense Parent Group",
                             "Offense Code", "MCPP", "Longitude", "Latitude"]).dropna()
    df['date2'] = pd.to_datetime(df['Offense Start DateTime'])
    df['Year'] = df['date2'].dt.year
    df['Month'] = df['date2'].dt.month
    df['Day'] = df['date2'].dt.day
    df['Hour'] = df['date2'].dt.hour
    df = df.drop(['Offense Start DateTime'], axis=1) 
    df = df.drop(['date2'], axis=1) 
    df = df[df['Year'] >= 2010]
    return df

def get_zip_code(df, geolocator):
    location = geolocator.reverse((df['Latitude'], df['Longitude']))
    return location.raw['address']['postcode']

def add_zip_column(df, geolocator):
    df['zipcode'] = df.head().apply(lambda x: get_zip_code(x, geolocator), axis = 1)
    return df

def add_income(income_file_name, crime_data):
    income_data = pd.read_csv(income_file_name, usecols=["Zip Code", "Avg. Income/H/hold"]).dropna()
    income_data['Zip Code'] = income_data['Zip Code'].astype("Int64")
    crime_data['zipcode'] = pd.to_numeric(crime_data['zipcode'], errors='coerce')
    crime_data['zipcode'] = crime_data['zipcode'].astype("Int64")
    merged_data = crime_data.merge(income_data, left_on = 'zipcode', right_on = 'Zip Code')
    test = merged_data.head()
    print(test)
    return merged_data

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

def main():
    cleaned_crime_data = preprocess_crime_data('crime_analysis/SPD_Crime_Data.csv')
    geolocator = geopy.Nominatim(user_agent='myusername')
    zip_crime_data = add_zip_column(cleaned_crime_data, geolocator)
    income_crime_data = add_income('crime_analysis/median_income.csv', zip_crime_data)

if __name__ == "__main__":
    main()
