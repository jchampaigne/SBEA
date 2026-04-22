#!/usr/bin/env python
# coding: utf-8

# # Concat Files
# ## Combines modules to make the full Consolidated list with mailing labels

# In[1]:


import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import re
from Fix_City_Names_Program import fix_city_names
from Mailing_Label_Program import mailing_label
from Consolidated_Compiler import *
import csv


# In[3]:


def main():        
    
    consolidated_list = concat_all_files()
    consolidated_list = fix_city_names(consolidated_list)
    consolidated_list = mailing_label(consolidated_list)
    print("All data processed.")
    
    # Save to file
    save_csv(consolidated_list)  
    
if __name__ == "__main__":
    main()


# In[ ]:




