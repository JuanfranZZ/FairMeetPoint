import streamlit as st
import pandas as pd

from utils import mean_location, distance_from_ref, get_pois

from geographiclib.geodesic import Geodesic
import osmnx as ox
import folium
from folium import plugins
from streamlit_folium import st_folium
from streamlit_folium import folium_static

from tqdm import tqdm

st.set_page_config(layout="wide")

st.title("Meetpoint")

col1, col2 = st.columns(2)

with col1:
    # number of origin points
    number = st.number_input(
        "Number of points", value=0, placeholder="Type the number of participants...", step= 1, min_value=0)
    st.write("The current number is ", number)
    
with col2:
    selector = st.selectbox('Type of input', ['City', 'Coordinates'])
    
    if selector == 'City':
        orig_point_text = 'City'
    elif selector == 'Coordinates':
        orig_point_text = 'Latitude, Longitude'
        
if number>0:
    st.subheader('Origin points')

# data of each origin point
orig_point = []
orig_point_name = []

col1, col2 = st.columns(2)

with col1:
    for i in range(number):
        orig_point_name.append(st.text_input(f"origin_{i+1} - name", value=None, placeholder="Name"))
    
with col2:
    for i in range(number):
        orig_point.append(st.text_input(f"origin_{i+1} - {orig_point_text}", value=None, placeholder=orig_point_text))
    

if all(orig_point) and number>0:
    
    # list of categories
    
    st.subheader('Meeting point setup')
    
    chosen_category = st.selectbox('Choose your category', 
                                   ('amenity', 'sport', 'leisure'))
    if chosen_category == 'amenity':
        list_tags = ['bar', 'restaurant', 
                    'arts centre', 'bus station', 
                    'casino', 'car rental', 'cinema', 
                    'convention centre', 'events centre',
                    'gym', 'hotel', 'juice bar', 'kiosk', 'library', 
                    'park', 'planetarium', 'sauna', 'shop', 'spa', 'nightclub', 'pub']
        
    elif chosen_category == 'sport':
        list_tags = ['climbing', 'soccer', 'billiards', 'darts', 'athletics', 'basketball',
                     'beachvolleyball', 'billiards', 'bmx', 'bowls', 'boxing', 'canoe', 'climbing_adventure', 'crossfit',
                     'cycling', 'dance', 'darts', 'fitness', 'golf', 'hiking', 'karting', 'kitesurfing', 'laser_tag',
                     'miniature_golf', 'multi', 'paddle_tennis', 'padel', 'paintball', 'parachuting', 'parkour',
                     'pelota', 'pickleball', 'pilates', 'racquet', 'roller_skating', 'running', 'scuba_diving',
                     'shooting', 'skateboard', 'squash', 'surfing', 'swimming', 'table_tennis', 'table_soccer',
                     'tennis', 'trampoline', 'ultimate', 'volleyball', 'water_polo', 'water_ski', 'windsurfing', 'yoga']
        
    elif chosen_category == 'leisure':
        list_tags = ['sports_centre', 'sports_hall', 'stadium',
                     'swimming_pool', 'recreation_ground',
                     'golf_course', 'fitness_centre']
        
    chosen_tag = st.selectbox('Choose your tag', list_tags)
    
    # Define tags to search
    tags = {chosen_category: chosen_tag}
    
    # select distance
    #distance = st.number_input(label='Distance (m)', min_value=0, value='min', step=1)
    distance = st.slider(label='Distance (m)', min_value=100, max_value=50000, value=1000, step=100)
        
    calculate = st.button("Calculate")
    if calculate:
        if selector == 'Coordinates':
            Latitude = [float(lat.split(',')[0]) for lat in orig_point]
            Longitude = [float(lon.split(',')[1]) for lon in orig_point]
        elif selector == 'City':
            Latitude = []
            Longitude = []
            for point in orig_point:
                Latitude.append(ox.geocode_to_gdf(point).centroid.get_coordinates()['y'].values[0])
                Longitude.append(ox.geocode_to_gdf(point).centroid.get_coordinates()['x'].values[0])

        coordinates = {}  # origin points and meetpoint
        
        for i in range(number):
            coordinates[orig_point_name[i]] = {"Latitude": Latitude[i], "Longitude": Longitude[i], "colour": "#0044ff"}


        # meetpoint
        #mp1 = meetpoint([(l[0], l[1]) for l in list(zip(Latitude, Longitude))])
        #coordinates['meetpoint1'] = {"Latitude": mp1[0], "Longitude": mp1[1], "colour":"#ff0033"}
        
        mp = mean_location(pd.DataFrame(coordinates).transpose())
        coordinates['meetpoint'] = {"Latitude": mp[0], "Longitude": mp[1], "colour":"#B200ED"}
        
        with st.expander("Points details"):
        
            col1, col2 = st.columns(2)
            
            # table showing data
            df = pd.DataFrame(coordinates).transpose()
            
            with col1:
                st.table(df[['Latitude','Longitude']])
            
            with col2:
                # map for coordinates points
                map1 = st.map(df, latitude='Latitude', longitude='Longitude', size=20, color='colour')
            
                print('Meetpoint spherical:')
                for k,v in coordinates.items():
                    distance_from_ref(k, (v['Latitude'], v['Longitude']), (coordinates['meetpoint']['Latitude'], coordinates['meetpoint']['Longitude']))
        
        
        # Second map with points of interest
        st.subheader('Map with points of interest')
   
        m = folium.Map(location=[coordinates['meetpoint']['Latitude'], coordinates['meetpoint']['Longitude']], zoom_start=15)
        
        folium.Circle(location=[coordinates['meetpoint']['Latitude'], coordinates['meetpoint']['Longitude']],
                      radius=distance, opacity=0.6, fill=True).add_to(m)
        
        pois = get_pois((coordinates['meetpoint']['Latitude'], coordinates['meetpoint']['Longitude']), tags=tags, distance=distance)

        if pois is None:
            # pois is None when not found
            st.warning(f'{chosen_tag} not found closer than {distance} from meetpoint!')
        else:
            for i, p in tqdm(pois.iterrows()):
                folium.Marker(location=[float(p['Latitude']),float(p['Longitude'])], 
                            tooltip=folium.Tooltip(p['name'], permanent=True)).add_to(m)
            
            for k, v in coordinates.items():
                if 'meet' not in k:
                    color='green'
                    icon_='bookmark'
                else:
                    color='purple'
                    icon_='flag'
                    
                folium.Marker(location=[float(v['Latitude']), float(v['Longitude'])],
                            tooltip=folium.Tooltip(k, permanent=True), 
                            icon=folium.Icon(icon=icon_, color=color)).add_to(m)
                
            screen_width = st.screen_width
            map_a = folium_static(m, width=screen_width, height=800)
        
        
        
        
        
        
    



