import pandas as pd
import numpy as np
import os
import glob
import time

districts_karnataka = [
    "Bagalkote", "Bellary", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", 
    "Bidar", "Chamarajanagar", "Chikballapur", "Chikkamagaluru", "Chitradurga", 
    "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan", 
    "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", 
    "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", 
    "Tumakuru", "Udupi", "Uttara Kannada", "Vijayanagara", "Vijayapura", 
    "Yadgir"
]
district_files = {}
def class_strength(student_num):
    if student_num > 0 and student_num <= 5 :
        return "0-5"
    elif student_num > 5 and student_num <= 10 :
        return "5-10"
    elif student_num > 10 and student_num <= 15 :
        return "10-15"
    else:
        return "15+"

def top_25(merged_df,district_name):
    print("IN TOP 25 SCHOOLS AND GPS ANALYSIS")

    #school analysis
    school = merged_df.groupby(['Block', 'Cluster','GPName', 'GP Id','DiseCode','SchoolName']).agg({'name_identifier':'count', 'Total Score of the Child': 'sum','Grade':'nunique'}).reset_index()
    school.columns = ['Block', 'Cluster','GPName', 'GP Id','DiseCode','SchoolName','Number of Students','Sum of All Scores','Grade_Count']

    
    school['Avg_Score'] = school['Sum of All Scores']/school['Number of Students']
    school['Criteria'] = merged_df['name_identifier'].count()/merged_df['DiseCode'].nunique()
    school['Criteria'] = school['Criteria'].astype('int64')

    print("School group by object:")
    print(school.head())

    school = school[school['Number of Students'] > school['Criteria']]

    #school['Class_Strength'] = school['Number of Students'].apply(class_strength)
    top25_sorted = school.sort_values(by = 'Avg_Score', ascending = False)
    print("TOP 25 SORTED SCHOOLS",top25_sorted.head())

    #save the output to a file
    output_filename = f"Top25Schools_{district_name}.csv"
    top25_sorted.to_csv(output_filename,index = False)

    # top 25 gps
    gps = merged_df.groupby(['Block', 'Cluster','GP Id','GPName']).agg({'name_identifier':'count', 'Total Score of the Child': 'sum'}).reset_index()
    gps.columns = ['Block', 'Cluster','GP Id','GPName','Number of Students','Sum of All Scores']

    gps['Avg_Score'] = gps['Sum of All Scores']/gps['Number of Students']
    gps['Criteria'] = merged_df['name_identifier'].count()/merged_df['GP Id'].nunique()
    gps['Criteria'] = gps['Criteria'].astype('int64')

    gps = gps[gps['Number of Students'] > gps['Criteria']]

    top25gps_sorted = gps.sort_values(by = 'Avg_Score', ascending = False)
    print("TOP 25 SORTED GPS",top25gps_sorted.head())

    output_filename = f"Top25GPs_{district_name}.csv"
    top25gps_sorted.to_csv(output_filename,index = False)















