import pandas as pd
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

def select_file(title):
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=[("CSV files", "*.csv")]
    )
    return file_path
    
def save_csv(consolidated_list, default_name="SBEA_current_mailing_list.csv"):

    # Ask the user where to save the file
    file_path = filedialog.asksaveasfilename(
        title="Save Mailing Labels",
        defaultextension=".csv",
        initialfile=default_name,
        filetypes=[("CSV files", "*.csv")]
    )

    if file_path:
        consolidated_list.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)
        print(f"File saved to: {file_path}")
    else:
        print("Save cancelled.")

def apply_label():
    file_path = select_file("Select Consolidated File")
    if not file_path:
        messagebox.showinfo("Cancelled", "No file selected.")
        return None
    
    df = pd.read_csv(file_path)    
    
    # Replace all NaNs with empty strings globally
    df = df.fillna('')

    # Define the labeling logic inside a lambda for each row
    df['Mailing Address'] = df.apply(
        lambda row: (
            # Member Type Filter (Make labels for Classmates or Teachers only, no deceased)
            "" if str(row['Member Type']) not in ['Classmates', 'Teachers'] else
            # Address Filter (Skip if blank)
            "" if not str(row['Address']).strip() else
            # Process and join valid lines
            "\n".join([
                line for line in [
                    f"{row['First Name']} {str(row['Married Name']).strip() or str(row['Last Name']).strip()}", # Name Line
                    str(row['Address']).strip(),                                                              # Address 1
                    str(row['Address2']).strip(),                                                             # Address 2
                    f"{row['City']}, {row['State']} {row['Zip']}",                                            # City/State/Zip
                    "" if str(row['Country']) == 'USA' else str(row['Country']).strip()                       # Country (Skip USA)
                ] if line.strip()
            ])
        ), 
        axis=1
    )

    return df

def create_labels():
    df = apply_label()
    if df is not None:
        save_csv(df)

def main():
    df = create_labels()

if __name__ == "__main__":
    main()

