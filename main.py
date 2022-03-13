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

def main():
    cleaned_crime_data = preprocess_crime_data('crime_analysis/SPD_Crime_Data.csv')
    geolocator = geopy.Nominatim(user_agent='myusername')
    zip_crime_data = add_zip_column(cleaned_crime_data, geolocator)
    income_crime_data = add_income('crime_analysis/median_income.csv', zip_crime_data)

if __name__ == "__main__":
    main()
