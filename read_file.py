import pandas as pd
import os
#import matplotlib.pyplot as plt
#import seaborn as sns
from block_gen_participation import blockwise_gen_participate
#from overall_score import overall_score_bracket
from overallscore_gender import score_gender
from competency_gen import competency_gender
#from competency_gen_excel import competency_gender_excel
from top25 import top_25
import glob
import os

district_files = {}
district_mapping = {}

def combine_district_data(district_name):
    global district_files
    required_columns = ['State', 'District', 'Block', 'Cluster', 'GPName', 'GP Id',
                        'SchoolName', 'SchoolId', 'DiseCode', 'QuestionGroup Id',
                        'QuestionGroupName', 'Source Name', 'Date of Visit',
                        'Academic Year of Visit', 'Group Value', 'RespondentType', 
                        'UserType', 'UserMobileNumber', 'Grade', 'Gender', 
                        'identifier', 'name_identifier', 'Total Score of the Child']

    all_grades_data = []
    for grade in ['4', '5', '6']:
        if grade in district_files[district_name]:
            df_grade = district_files[district_name][grade][required_columns]
            all_grades_data.append(df_grade)
        else:
            print(f"Warning: Grade {grade} not found for district {district_name}")
            return False

    combined_df = pd.concat(all_grades_data, axis=0)
    print("\nData Inspection:")
    print("1. Column types:")
    print(combined_df.dtypes)
    
    print("\n2. Sample of Total Score column:")
    print(combined_df['Total Score of the Child'].head())
    
    print("\n3. Unique values in Total Score column:")
    print(combined_df['Total Score of the Child'].unique())
    
    print("\n4. Any non-numeric values:")
    if combined_df['Total Score of the Child'].dtype == 'object':
        non_numeric = combined_df[pd.to_numeric(combined_df['Total Score of the Child'], errors='coerce').isna()]
        print(f"Found {len(non_numeric)} non-numeric values:")
        print(non_numeric['Total Score of the Child'].unique())

    print(f"Shape of combined dataframe for district {district_name}: {combined_df.shape}")
    combined_df.to_csv(f"combined_data_{district_name}.csv", index=False)
    print(f"Combined data saved for district {district_name}")
    return combined_df

def store_district_data(df, grade, district_name):
    global district_files
    if district_name not in district_files:
        district_files[district_name] = {}

    district_files[district_name][grade] = df
    print(f"Stored data for district: {district_name}, grade: {grade}") 

def preprocess_csv(full_main_path,full_comp_path,grade,dir_name,district_name):
    try:
        print("DISPLAYING MAIN TABLE FROM PROCESS MODULE")
        df = pd.read_csv(full_main_path)
        df = df[df['Block'] != 'bangarapete']
        print(df.head())

        columns_to_caps = ['District','Block','Cluster']
        df[columns_to_caps] = df[columns_to_caps].apply(lambda x: x.str.title())
        print("COLUMNS AFTER FIRST LETTER CAPS:",df[columns_to_caps])

        #df['Block'] = df['Block'].str.replace(r'[^\w\s]', '', regex=True)
        df['Block'] = df['Block'].str.title()
        df['Block'] = df['Block'].replace("Kgf", "KGF")

        #calling function to combine district wise data
        store_district_data(df, grade, district_name)
        print("LENGTH OF DISTRICT KEY:",len(district_files[district_name]))
        if len(district_files[district_name]) == 3:
            merged_df = combine_district_data(district_name)
            top_25(merged_df,district_name)

        print("DISPLAYING COMPETENCY TABLE FROM PROCESS MODULE")
        compdf = pd.read_csv(full_comp_path)
        print(compdf.head())

        #grouped_data_gender = df.groupby(['District', 'Block', 'Gender'])['name_identifier'].count().reset_index(name='Count')
        #print(grouped_data_gender)


        competency_gender(df,compdf,grade,dir_name)

        #competency_gender_excel(df,compdf,grade,dir_name)



        blockwise_gen_participate(df,grade,dir_name)

        

        score_gender(df,grade,dir_name)

        

        #return head
    except Exception as e:
        print(f"Error: ",e)  
        raise  














        