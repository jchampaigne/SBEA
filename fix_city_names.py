# Fix City Names Program
# Standardizes city names entered by members
# Saves a list of cities to be corrected or added to the master list

import pandas as pd
import re


# Normalize City Names to Allow Better Matching
def normalize_location(location):
    """
    Normalize location strings by standardizing abbreviations, removing punctuation,
    and eliminating spaces.
    
    Args:
        location: The location string to normalize. Can be None or NaN.
        
    Returns:
        The normalized location string or the original value if it was None/NaN.
    """
    if pd.isna(location):
        return location
    
    # Convert to lowercase and remove leading/trailing whitespace
    normalized = location.lower().strip()

    # Standardize common abbreviations
    abbreviation_map = {
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

    for pattern, replacement in abbreviation_map.items():
        normalized = re.sub(pattern, replacement, normalized)

    # Remove punctuation
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)

    # Collapse multiple spaces into a single space
    normalized = re.sub(r'\s+', ' ', normalized)

    # Remove all spaces (e.g., "La Paz" → "lapaz")
    normalized = normalized.replace(" ", "")

    return normalized.strip()

def create_location_norm(df):
    
    #Adds a 'location_norm' column to the DataFrame
    
    # Initialize the column
    df['location_norm'] = None
    
    # Create a mask for USA rows
    #mask = df['Country'].eq('USA')
    
    cities = df['City'].fillna('').astype(str).apply(normalize_location)
    states = df['State'].fillna('').astype(str)

    df['location_norm'] = cities + ', ' + states
    
    return df

def save_misspelled_cities(consolidated_list, df_cities):
    df_misspelled = consolidated_list[
    (~consolidated_list['location_norm'].isin(df_cities['location_norm'])) &
    (consolidated_list['Country'] == 'USA')]
    df_misspelled = df_misspelled.sort_values(by = ['School', 'Year', 'Last Name', 'First Name'])
    
    return df_misspelled

def merge_data(consolidated_list, df_cities):
    # Drop duplicates - some states have two cities with same exact name
    df_cities = df_cities.drop_duplicates(subset=['location_norm'])
    # Pass both dfs in so the function can see them
    return consolidated_list.merge(
        df_cities[['location_norm', 'City', 'State']], 
        on="location_norm", 
        how="left", 
        suffixes=('', '_std')
    )

def replace_city_names(df):
    # Identify where a standardized match was found
    mask = df['City_std'].notna()
    
    # Replace original City/State with the standardized ones
    df.loc[mask, 'City'] = df.loc[mask, 'City_std']
    df.loc[mask, 'State'] = df.loc[mask, 'State_std']
    
    # Drop the extra helper columns
    return df.drop(columns=['City_std', 'State_std'])

def fix_city_names(df):
    # To be run in other programs
    df_cities = pd.read_csv('uscities.csv')
    
    # Normalize names
    df = create_location_norm(df)
    df_cities = create_location_norm(df_cities)
    df_cities = df_cities.drop_duplicates(subset=['location_norm'], keep='first')
    
    # Misspelled Cities Report
    df_misspelled = save_misspelled_cities(df, df_cities)
    report_path = '/Users/champ/Documents/SBAA/SBAA_Data_Analysis/Misspelled_Cities.xlsx'
    df_misspelled.dropna(subset=['City']).drop(columns=['location_norm']).to_excel(report_path, index=False)
   
    # Merge & Replace
    df = merge_data(df, df_cities)
    df = replace_city_names(df)
    
    # Drop helper columns and blank cities
    #df = df.dropna(subset=['City']).drop(columns=['location_norm'], errors='ignore')
    df_fixed_city_names = df.drop(columns=['location_norm'], errors='ignore')
    
    return df_fixed_city_names

# ---- MAIN ----
def main():
    consolidated_list = pd.read_csv('Consolidated_05_2026_raw.csv', low_memory=False)
    df_cities = pd.read_csv('uscities.csv')
    
    consolidated_list = create_location_norm(consolidated_list)
    df_cities = create_location_norm(df_cities)
    df_cities = df_cities.drop_duplicates(subset=['location_norm'], keep='first')
    
    df_misspelled = save_misspelled_cities(consolidated_list, df_cities)
    df_misspelled.dropna(
        subset=['City']).drop(columns=['location_norm']).to_excel('/Users/champ/Documents/SBAA/SBAA_Data_Analysis/Misspelled_Cities.xlsx', index=False)
   
    consolidated_list = merge_data(consolidated_list, df_cities)
    consolidated_list = replace_city_names(consolidated_list)
    
    consolidated_list.drop(columns=['location_norm']).to_csv('fix_city_names_test.csv', index=False)
    print(f"Successfully processed and saved")

    #return df
    
if __name__ == "__main__":
    main()

