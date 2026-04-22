#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import csv

def create_label(row):
    # 2. Member Type Filter (Classmates or Teachers only)
    if str(row['Member Type']) not in ['Classmates', 'Teachers']:
        return ""

    # 3. Address Filter (Skip if blank)
    addr = str(row['Address']).strip()
    if not addr:
        return ""

    # 4. Name Logic (Married Name priority)
    m_name = str(row['Married Name']).strip()
    last = m_name if m_name else str(row['Last Name']).strip()
    name_line = f"{row['First Name']} {last}"

    # 5. Address2, City/State/Zip, and Country (Skip if USA)
    addr2 = str(row['Address2']).strip()
    csz_line = f"{row['City']}, {row['State']} {row['Zip']}"
    
    country = str(row['Country'])
    if country == 'USA':
        country = ""
    
    # 6. Consolidate lines (joins only the non-empty strings)
    lines = [name_line, addr, addr2, csz_line, country]
    return "\n".join([line for line in lines if line.strip()])

def mailing_label(df):
    # To be used in other file
    # Replace all NaNs with empty strings globally
    df = df.fillna('')
    df['Mailing Address'] = df.apply(create_label, axis=1)

    return df

def main():
    # Replace all NaNs with empty strings globally
    df = pd.read_csv('/Users/champ/Documents/SBAA/Consolidated_04_2026.csv')
    df = df.fillna('')
    df['Mailing Address'] = df.apply(create_label, axis=1)
    df.to_csv('/Users/champ/Documents/SBAA/Mailing_Label_Test.csv', index=False)

if __name__ == "__main__":
    main()


# In[ ]:




