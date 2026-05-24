# SBEA Monthly Stats
# Takes the individual monthly stats and transforms the data so it can be plotted over time

import pandas as pd
import calendar
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

def select_folder_path(title='Select folder where Monthly Stats are saved'):
    selected_folder = filedialog.askdirectory(title=title)
    
    if selected_folder:
        folder_path = Path(selected_folder)
        excel_files = list(folder_path.glob("*.xlsx"))

        if not excel_files:
            messagebox.showwarning("No .xlsx files found in the selected folder.")
            return None, []
    
        return selected_folder, excel_files
    
    return None, []

def group_files(excel_files):
    df_list = []

    # Generate month labels: Jan 2025, Feb 2025, ...
    start_year = 2025
    start_month = 1
    month_labels = []

    for i in range(len(excel_files)):
        month_number = start_month + i
        year = start_year + (month_number - 1) // 12
        month = ((month_number - 1) % 12) + 1
        month_name = calendar.month_abbr[month]
        month_labels.append(f"{month_name} {year}")

    for i, file in enumerate(excel_files):
        df = pd.read_excel(file, nrows=7)
        df["Date"] = month_labels[i]   # correct month
        df_list.append(df)

    # Append vertically (row-wise)
    combined = pd.concat(df_list, ignore_index=True)

    return combined

def save_csv(df, default_name="SBEA_combined_stats.xlsx"):
    if df.empty:
        messagebox.showinfo('Error', 'No data to save.')
        return
    
    # Ask the user where to save the file
    file_path = filedialog.asksaveasfilename(
        title="Save Monthly Stats",
        defaultextension=".xlsx",
        initialfile=default_name,
        filetypes=[("Excel files", "*.xlsx")]
    )

    if file_path:
        df.to_excel(file_path, index=False)
        print(f"File saved to: {file_path}")
    else:
        print("Save cancelled.")

# ---- MAIN ----

def main():
    root = tk.Tk()
    root.withdraw()

    selected_folder, excel_files = select_folder_path(
        'Select folder with Excel Files'
    )
    
    if not selected_folder or not excel_files:
        messagebox.showinfo("Cancelled", "No file selected.")
        return

    combined = group_files(excel_files)
    save_csv(combined)

if __name__ == "__main__":
    main()
