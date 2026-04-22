# Consolidated Compiler Program v3
# Module for combining classmate and teacher lists from all 7 schools

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import re
from Fix_City_Names import fix_city_names
from Mailing_Label_Program import mailing_label
import csv


# ---- UTILITY ----
selected_columns = [
    'School', 'Member Type', 'Year', 'First Name', 'Last Name', 'Married Name', 
    'Email', 'Address', 'Address2', 'City', 'State', 'Zip', 'Country', 
    'Telephone', 'Cell Phone', 'Last Login', 'Joined On', 'Year Deceased', 
    'Last Updated', 'Spouse/Partner', 'Birth Month', 'Birth Day', 'Birth Year', 
    'Elementary School', 'Military Service (Branch)', 'Buddy', 'Any Siblings?'
]

def select_file(title):
    return filedialog.askopenfilenames(
        title=title,
        filetypes=[("CSV files", "*.csv")]
    )
    
def save_csv(consolidated_list, default_name="consolidated_list.csv"):

    # Ask the user where to save the file
    file_path = filedialog.asksaveasfilename(
        title="Save Consolidated List CSV",
        defaultextension=".csv",
        initialfile=default_name,
        filetypes=[("CSV files", "*.csv")]
    )

    if file_path:
        consolidated_list.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)
        print(f"File saved to: {file_path}")
    else:
        print("Save cancelled.")
        

# ---- CLASSMATE WORKFLOW ----

def process_classmate_files():
    classmate_files = select_file("Select Classmate CSV Files")
    if not classmate_files:
        messagebox.showinfo("Cancelled", "No classmate files selected.")
        return None

    #convert_file_to_UTF(classmate_files)

    dataframes = []
    for file_path in classmate_files:
        file_name = os.path.basename(file_path)
        df = pd.read_csv(file_path, encoding='latin-1', low_memory=False)
        df['School'] = os.path.splitext(file_name)[0]
        df.insert(0, 'School', df.pop('School'))
        df = df[selected_columns]       
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)

# ---- TEACHER WORKFLOW ----

def process_teacher_files():
    teacher_files = select_file("Select Teacher CSV Files")
    if not teacher_files:
        messagebox.showinfo("Cancelled", "No teacher files selected.")
        return None

    #convert_file_to_UTF(teacher_files)

    dataframes = []
    for file_path in teacher_files:
        file_name = os.path.basename(file_path)
        df = pd.read_csv(file_path, encoding='latin-1', low_memory=False)
        df.insert(1, 'Year', '')  # Add blank Year column
        df['School'] = os.path.splitext(file_name)[0]
        df.insert(0, 'School', df.pop('School'))
        df = df[selected_columns]
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)

def concat_all_files():
    root = tk.Tk()
    root.withdraw()
    
    # Combine all Classmate files
    all_classmates = process_classmate_files()
    if all_classmates is None:
        return
    # Combine all Teacher files
    all_teachers = process_teacher_files()
    if all_teachers is None:
        return
    
    # Combine the two into one main df
    consolidated_list = pd.concat([all_classmates, all_teachers], ignore_index=True)
    
    # Ensure classmates with last name of 'True' remain a string and not a Boolean
    consolidated_list['Last Name'] = consolidated_list['Last Name'].apply(
    lambda x: f'="{x}"' if str(x).upper() == "TRUE" else x 
    )
    
    print("All data bundled.")
    
    return consolidated_list
    
# ---- MAIN ----
def main():
    test = concat_all_files()
    # Save to file
    save_csv(test)
    
if __name__ == "__main__":
    main()






