from copy import deepcopy
import pandas as pd
import streamlit as st
from haversine import haversine
import psycopg2

#fetch nums of assined riders
conn = psycopg2.connect(database="<db-name>",
                        user = "<username>",
                        password = "<password>",
                        host = "<address>",
                        port = "<port-number>")
cur = conn.cursor()

cur.execute(" SELECT agentphone FROM tickets where state_id = 2 ");
t = cur.fetchall()
nums=[]
for i in t:
    if i[0]==None:
        continue
    for j in i[0].split(','):
        try:
            num = int(j)
            flag = True
        except :
            flag = False
        if flag:    
            nums.append(j)
conn.close()


st.title("Find Closest Relief Rider")
display = ("Bengaluru", "Pune","Jaipur","Guwahati")
options = list(range(len(display)))
value = st.selectbox("Select City", options, format_func=lambda x: display[x])

if value==0: #BLR
    Url = "<link>" 
elif(value==1): #PUNE
    Url = "<link>" 
elif(value==2): #JPR
    Url = "<link>" 
elif(value==3): #GWH
    Url = "<link>" 

@st.cache(ttl=3600)

def load_data(url=Url):
    df = pd.read_csv(url)    
   
    # Location Format Conversion
    if value==0 or value==1:
        LatLong = "GPS Coordinates of your location or Nearest Landmark"
    else:
        LatLong = "Lat/lon (get from google maps)"
    df[["lat", "lon"]] = df[LatLong].str.split(",", expand=True)
    df.lat = df.lat.astype(float)
    df.lon = df.lon.astype(float)

    # Filter Data
    df = df[df.Status == "Active"]
    print(df)
    
    return df


# Load data and make a copy
data = load_data()

df = deepcopy(data)

params = st.experimental_get_query_params()
try:
    input_value=params['latlon'][0]
except KeyError :
    if value==0:
        input_value='12.978339208542025, 77.59252543225985'
    elif value==1:
        input_value='18.523434607136984, 73.87224367735865'
    elif value==2:
        input_value='26.923657693391295, 75.7912931287796'
    elif value==3:
        input_value=' 26.14596544311235, 91.73104600479064'

# Input
help_input = st.text_input(
    label="Request Location",
    help="Enter lat, lon as comma separated value",
    value=input_value
)
help_loc = help_input.split(",")
lat = float(help_loc[0].strip())
lon = float(help_loc[1].strip())
help_loc = (lat, lon)

rider_count = 10
st.subheader(f"Your {rider_count} Closest riders are:")

# Compute
def get_distance(row):
    loc = (row["lat"], row["lon"])
    dist = haversine(help_loc, loc)
    return dist


# Main Data Render
def sort_and_display(df, rider_count: int):
    df = pd.DataFrame(df,columns=['Name of Relief Rider','Phone number','Total Sorties','lat','lon'])
    df.set_index("Name of Relief Rider",inplace=True)
    df["Distance(Km)"] = df.apply(get_distance,axis=1)
    sorted_df = df.sort_values(by="Distance(Km)", ascending=True)
    cols = sorted_df.columns.tolist()
    columns = ["Distance(Km)"] + cols[:4]
    sorted_df = sorted_df[columns]
    return sorted_df[:rider_count]


st.table(sort_and_display(df, rider_count=rider_count))
