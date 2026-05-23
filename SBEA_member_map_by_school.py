# SBAA Member Map
# Totals the number of active members for each school and city and places a marker on a map

import pandas as pd
import numpy as np
import folium
from folium import plugins
from pandas import Series, DataFrame
import tkinter as tk
from tkinter import filedialog, messagebox
from helper_functions import *
from fix_city_names import fix_city_names
from get_coordinates import *

def select_file(title):
    # Ask user which consolidated file to use
    return filedialog.askopenfilename(
        title=title,
        filetypes=[("CSV files", "*.csv")]
    )
    
def save_html(folium_map, default_name="SBEA_map_active_members.html"):
    # Ask user where to save the file
    file_path = filedialog.asksaveasfilename(
        title="Save map",
        defaultextension=".html",
        initialfile=default_name,
        filetypes=[("HTML files", "*.html")]
    )

    if file_path:
        folium_map.save(file_path)
        print(f"File saved to: {file_path}")
    else:
        print("Save cancelled.")

def create_table(df):
    df['Location'] = df['City'] + ', ' + df['State']
    df['Location'] = np.where(df['Country'] != 'USA', df['Country'], df['Location'])

    df_table = pd.crosstab(
        index= df['Location'], 
        columns=df['School'], 
        margins=True, 
        margins_name='Total')
    
    return df_table

def create_map(df_coord_table):
    # Initialize map (centered on the US)
    member_map = folium.Map(location=[39.8283, -98.5795],tiles='CartoDB positron', zoom_start=4)

    # instantiate a mark cluster object for the incidents in the dataframe
    map_marker = plugins.MarkerCluster().add_to(member_map)

    # Loop through the DataFrame and add markers
    for Location, row in df_coord_table.iterrows():
        lat = row['lat']
        lng = row['lng']

        # Create popup content
        popup_html = f"""
        <div style="font-size:16px;">
        <b>{row['Location']}</b><br>Total Active Members: {row['Total']}<br>"""
        for col in df_coord_table.columns:
            if col not in ['Location', 'lat', 'lng', 'Total']:
                popup_html += f"{col}: {row[col]}<br>"

        # Add marker
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(map_marker)

    return member_map

def process_file(df):
    # Clean the data
    df = active_member_locations(df)
    df = fix_city_names(df)
    
    # Create a summary table
    df_totals = create_table (df)
    # Drop 'Total' row to avoid geocoding errors
    #df_totals = df[:-1]
    
    df_coord_table = get_coordinates(df_totals)
    
    final_map = create_map(df_coord_table)
    return final_map

def run_map_program(df_raw):
    root = tk.Tk()
    root.withdraw()

    path = select_file("Select Consolidated File")
    if not path:
        messagebox.showinfo("Cancelled", "No file selected.")
        return
    
    generated_map = process_file(df_raw)
    save_html(generated_map)

    return generated_map


def main():
    # Load data
    df_raw = pd.read_csv('/Users/champ/Documents/SBAA/Consolidated_05_2026_raw.csv', low_memory=False)
    final_map = run_map_program(df_raw)
    
    if final_map is not None:
        final_map.save('map_test.html')

if __name__ == "__main__":
    main()
