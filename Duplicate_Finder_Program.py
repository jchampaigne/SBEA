#!/usr/bin/env python
# coding: utf-8

# # Duplicate Finder Program

# #### This will find duplicate names (or possible duplicates) so they can be removed.

# In[1]:


import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from rapidfuzz import fuzz


# In[3]:


# ---- UTILITY ----

def select_and_read_file(title):
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=[
            ("CSV and Excel files", "*.csv *.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls")
        ]
    )
    if not file_path:
        return None

    try:
        if file_path.lower().endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.lower().endswith((".xlsx", ".xls")):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file type.")
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def save_to_excel(df, default_name="SBEA_duplicates.xlsx"):
    file_path = filedialog.asksaveasfilename(
        title="Save SBEA Duplicates Excel File",
        defaultextension=".xlsx",
        initialfile=default_name,
        filetypes=[("Excel files", "*.xlsx")]
    )
    if file_path:
        df.to_excel(file_path, index=False)
        print(f"File saved to: {file_path}")
        return file_path
    else:
        print("Save cancelled.")
        return None

def after_save_workflow(df_current):
    root = tk.Tk()
    root.withdraw()

    result = messagebox.askyesno("Compare Files", "Do you want to show only new duplicates?")
    if not result:
        messagebox.showinfo("Done", "No comparison selected. Exiting.")
        root.quit()
        return

    df_previous = select_and_read_file("Select the previous Duplicates file")
    if df_previous is None:
        messagebox.showinfo("Cancelled", "No file selected. Exiting.")
        root.quit()
        return

    only_new = show_only_new(df_current, df_previous)
    if only_new is not None:
        save_to_excel(only_new, "Only_New_Duplicates.xlsx")

    root.quit()

def show_only_new(df_current, df_previous):
    key_cols = ['School', 'Year', 'First', 'Last Name']
    try:
        common = df_current.merge(df_previous, on=key_cols, how='inner')
        new_only = df_current[~df_current.set_index(key_cols).index.isin(common.set_index(key_cols).index)]
        return new_only
    except Exception as e:
        print(f"Error comparing files: {e}")
        return None

# ---- PROCESS FILE ----

def process_file(df_schools):
    df_schools = df_schools.dropna(axis=1, how='all')

    df_schools[['First', 'Middle']] = df_schools['First Name'].str.split(' ', n=1, expand=True)

    first = df_schools.pop('First')
    df_schools.insert(3, first.name, first)

    middle = df_schools.pop('Middle')
    df_schools.insert(4, middle.name, middle)

    df_schools = df_schools.drop(['First Name'], axis=1)

    # Define fuzzy matching threshold
    threshold = 85  # You can adjust based on strictness desired

    # Step 1: Group by exact-match fields
    grouped = df_schools.groupby(['School', 'Year', 'Last Name'])

    # Step 2: Check for fuzzy matches on 'First' within each group
    duplicates_idx = set()

    for _, group in grouped:
        first_names = group['First'].tolist()
        indices = group.index.tolist()
    
        for i in range(len(first_names)):
            for j in range(i + 1, len(first_names)):
                similarity = fuzz.ratio(first_names[i], first_names[j])
                if similarity >= threshold:
                    # Add both indices to the duplicates set
                    duplicates_idx.update([indices[i], indices[j]])
    
    # Step 3: Create and sort the duplicates DataFrame
    duplicates = df_schools.loc[list(duplicates_idx)]
    duplicates = duplicates.sort_values(by=['School', 'Year', 'Last Name', 'First'])
    
    return duplicates.reset_index(drop=True)

# ---- MAIN ----

def main():
    root = tk.Tk()
    root.withdraw()

    df = select_and_read_file("Select the Consolidated CSV file")
    if df is None:
        messagebox.showinfo("Cancelled", "No file selected.")
        return

    duplicate_rows = process_file(df)
    saved_path = save_to_excel(duplicate_rows)
    if saved_path:
        after_save_workflow(duplicate_rows)

if __name__ == "__main__":
    main()


# In[ ]:




