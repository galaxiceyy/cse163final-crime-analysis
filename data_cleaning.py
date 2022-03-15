import pandas as pd


def preprocess_crime_data(SPD_file_name):
    """
    Load in csv file. covert the offense start datatime into column
    filter the crime incidents occurred between 2018-2022.
    add zip code column from long/lat coordinates
    """
    chunk = pd.read_csv(SPD_file_name, chunksize=1000,
                        usecols=["Report Number",
                                 "Offense Start DateTime",
                                 "Report DateTime",
                                 "Offense Parent Group",
                                 "Offense Code", "Offense",
                                 "MCPP", "Longitude", "Latitude"])
    df = pd.concat(chunk)
    df['date2'] = pd.to_datetime(df['Offense Start DateTime'])
    df['Year'] = df['date2'].dt.year
    df['Month'] = df['date2'].dt.month
    df['Day'] = df['date2'].dt.day
    df['Hour'] = df['date2'].dt.hour
    df['Minute'] = df['date2'].dt.minute
    df = df.drop(['Offense Start DateTime'], axis=1)
    df = df.drop(['date2'], axis=1)
    df = df[df['Year'] >= 2016]
    df.to_csv('cleaned_crime_data.csv', index=False)


def main():
    preprocess_crime_data('SPD_Crime_Data.csv')


if __name__ == "__main__":
    main()
