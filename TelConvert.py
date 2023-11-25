
import numpy as np



# Define the conversion functions
def lat_to_meters(df):
    df_subset = df.dropna(subset=['lat'])
    ref_lat = df_subset['lat'].iloc[0]
    df['lat'] = df['lat'].apply(lambda lat: (lat - ref_lat) * 111000/100)  #/100 because currently it is like this in output csv
    return df

def lon_to_meters(df):
    print('convert')
    df_subset = df.dropna(subset=['lon','lat'])
    ref_lon = df_subset['lon'].iloc[0]
    ref_lat = df_subset['lat'].iloc[0]
    print(ref_lon)
    print(ref_lat)
    ref_lat_rad = np.radians(ref_lat)
    df['lon'] = df['lon'].apply(lambda lon: (lon - ref_lon) * 111000/100 * np.cos(ref_lat_rad))
    return df

converter = {'lat':lat_to_meters,'lon':lon_to_meters}
