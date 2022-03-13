import pandas as pd
import geopy
import csv

df = pd.read_csv('cleaned_crime_data.csv')

df = df.loc[(df["Longitude"] != 0) & (df["Latitude"] != 0) & (df['Year'] == 2020) & (df['Month'] == 12)]

from tqdm import tqdm
tqdm.pandas()
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="my_application")
from geopy.extra.rate_limiter import RateLimiter
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

df['Location'] = df.progress_apply(lambda row: reverse((row['Latitude'], row['Longitude'])), axis=1)

def parse_zipcode(location):
    if location and location.raw.get('address') and location.raw['address'].get('postcode'):
        return location.raw['address']['postcode']
    else:
        return None

df['Zipcode'] = df['Location'].apply(parse_zipcode)

df.to_csv('Crime_2020_With_Zip.csv', index=False)