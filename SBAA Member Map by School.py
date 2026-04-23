#!/usr/bin/env python
# coding: utf-8

# # SBAA Member Map

# ## Totals the active members for each city and places a marker on a map

# In[43]:


import pandas as pd
import numpy as np
import folium
from folium import plugins
from pandas import Series, DataFrame


# In[45]:


df = pd.read_csv('/Users/champ/Documents/SBAA/Consolidated_04_2026.csv', low_memory=False)

df.head(1)


# In[47]:


# Drop empty columns if needed
df=df.dropna(axis=1, how='all')
df.shape


# In[49]:


# Creates a new column called 'Active' that shows classmates or teachers who have joined and are not deceased

df.loc[:,'Active'] = np.where(((df['Member Type']== 'Classmates') | (df['Member Type']== 'Teachers')) 
                              & (df['Joined On'].str.contains('NaN')== False), 'Active', pd.NA)


# In[51]:


# Drops all records where 'Active' column is empty

df = df.dropna(subset=['Active'])
df.shape


# ### Normalize City Names to Allow Better Matching

# In[53]:


import re

def normalize_location(x):
    if pd.isna(x):
        return x
    
    x = x.lower().strip()

    # Standardize common abbreviations
    replacements = {
        r'\bft\b': 'fort',
        r'\bmt\b': 'mount',
        r'\bst\b': 'saint',
        r'\bste\b': 'sainte',
        r'\bhts\b': 'heights',
        r'\bpkwy\b': 'parkway',
        r'\bvly\b': 'valley',
        r'\bn\b': 'north',
        r'\bs\b': 'south',
        r'\be\b': 'east',
        r'\bw\b': 'west',
        r' & ': 'and'
    }

    for pattern, repl in replacements.items():
        x = re.sub(pattern, repl, x)

    # remove punctuation
    x = re.sub(r'[^a-z0-9\s]', '', x)

    # collapse multiple spaces
    x = re.sub(r'\s+', ' ', x)

    # remove all spaces so "La Paz" → "lapaz"
    x = x.replace(" ", "")

    return x.strip()


# In[55]:


df = df.copy()

df['location_norm'] = (
    df['City'].apply(normalize_location)
    .where(df['Country'].eq('USA'),
           df['Country'].apply(normalize_location))
)

df.head()


# In[139]:


df.to_csv('df_normalize.csv')


# In[57]:


# Combines city and state into one column, reduces dataframe to these columns

df_locations = df
df_locations.loc[:,'City_State'] = df['City'] + ', ' + df['State']
df_locations['Location'] = df.apply(lambda row: row['City_State'] if row['Country'] == 'USA' else row['Country'], axis=1)
df_locations['location_norm'] = df_locations['location_norm'].where(
    df_locations['Country'] != 'USA',
    df_locations['location_norm'] + ', ' + df['State'])
df_locations = df_locations[['School', 'Year', 'First Name', 'Last Name', 'Location', 'location_norm', 'Country', 'Active']].copy()
df_locations


# In[204]:


df_locations.to_csv('df_locations.csv', index=False)


# In[59]:


# Creates a table showing the number of active members for each school sorted by city

df_table = pd.crosstab(
    index=df_locations['Location'], 
    columns=df_locations['School'], 
    margins=True, 
    margins_name='Total')
df_table


# In[61]:


#Add location_norm back to df_table by merging a lookup

lookup = df_locations[["Location", "location_norm"]].drop_duplicates()

df_table = df_table.merge(
    lookup,
    left_index=True,      # Location is the index of df_table
    right_on="Location",   # match on lookup.Location
    how="left"
)
df_table


# In[23]:


df_table.to_csv('df_table.csv')


# In[63]:


# Import list of US coordinates
df_coord = pd.read_csv('uscities.csv', low_memory=False)
df_coord = df_coord[['City', 'State', 'lat', 'lng']]
df_coord.head()


# In[67]:


df_coord['location_norm'] = df_coord['City'].apply(normalize_location)
df_coord.head()


# In[69]:


# Combines city and state into one column

df_coord['Location'] = df_coord['City'] + ', ' + df_coord['State']
df_coord['location_norm'] = df_coord['location_norm'] + ', ' + df_coord['State']
df_coord = df_coord[['Location', 'location_norm', 'lat', 'lng']].copy()
df_coord.head()


# In[71]:


# Finds which members were not assigned a coordinate so we can add it to the df_coord list or fix spelling on the website

df_missing = df_locations[
    (~df_locations['location_norm'].isin(df_coord['location_norm'])) &
    (df_locations['Country'] == 'USA')]
df_missing = df_missing.sort_values(by = ['School', 'Year', 'Last Name', 'First Name'])
df_missing


# In[33]:


df_missing.to_excel('/Users/champ/Documents/SBAA/SBAA_Data_Analysis/df_missing.xlsx')


# In[73]:


# Read CSV file with central coordinates for each country

df_country_coord = pd.read_csv('Country_Coordinates.csv')
df_country_coord.head()


# In[75]:


df_country_coord['location_norm'] = df_country_coord['Location'].apply(normalize_location)
df_country_coord.head()


# In[77]:


# Combines US coordinates and World coordinates into one dataframe

df_all_coord = pd.concat([df_coord, df_country_coord])
df_all_coord


# In[41]:


df_all_coord.to_csv('df_all_coord.csv')


# In[79]:


# Combines coordinates dataframe with active members dataframe 
# so there are now coordinates for each city or country where there is an active member

#merged_df = pd.merge(df_table, df_all_coord, on = 'location_norm', how = 'left', suffixes =('_locations', '_coord'))
#merged_df

# Merge df_table with coordinates using location_norm

merged_df = df_table.merge(
    df_all_coord,
    on="location_norm",
    how="left",
    suffixes=("_table", "_coord")
)
merged_df


# In[119]:


merged_df.to_csv('merged_df_1.csv', index=False)


# In[81]:


# Restore the original preferred spelling from df_all_coord

merged_df["Location_final"] = merged_df["Location_coord"].fillna(merged_df["Location_table"])
merged_df


# In[83]:


# Group by normalized name and SUM the numeric columns
numeric_cols = merged_df.select_dtypes(include="number").columns.tolist()

merged_df = merged_df.groupby("location_norm", as_index=False).agg(
    {**{col: "sum" for col in numeric_cols},
     **{"Location_final": "first", "lat": "first", "lng": "first"}}
)
merged_df


# In[85]:


# Clean up extra columns

merged_df = merged_df.drop(columns=[
    "Location_table", "Location_coord"
], errors="ignore")

# Reorder columns 
cols = ["Location_final", "location_norm"] + [
    c for c in merged_df.columns if c not in ["Location_final", "location_norm"]
]
merged_df = merged_df[cols]
merged_df = merged_df.dropna(subset=['lat', 'lng'])
merged_df


# In[62]:


merged_df.to_csv('merged_df.csv', index=False) 


# # Use Crosstab in Map

# In[87]:


# Initialize map (centered on the US)
map = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# instantiate a mark cluster object for the incidents in the dataframe
map_marker = plugins.MarkerCluster().add_to(map)

# Loop through the DataFrame and add markers
for Location, row in merged_df.iterrows():
    lat = row['lat']
    lng = row['lng']
    
    # Create popup content
    popup_html = f"""
    <div style="font-size:16px;">
    <b>{row['Location_final']}</b><br>Total Active Members: {row['Total']}<br>"""
    for col in merged_df.columns:
        if col not in ['Location_final', 'location_norm', 'lat', 'lng', 'Total']:
            popup_html += f"{col}: {row[col]}<br>"
    
    # Add marker
    folium.Marker(
        location=[lat, lng],
        popup=folium.Popup(popup_html, max_width=250)
    ).add_to(map_marker)

# Show the map
map


# In[89]:


map.save('/Users/champ/Documents/SBAA/SBAA_Data_Analysis/SBEA_map_active_members.html')


# In[ ]:




