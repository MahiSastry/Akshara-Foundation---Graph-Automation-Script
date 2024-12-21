import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
from kannada_transl import english_to_kannada
import plotly
import plotly.express as px
import plotly.graph_objects as go
import kaleido

def get_question_file():
    pass

def competency_gender(df,compdf,grade,dir_name):
    print("competency_gender function has been called")
    # i'm only interested in csv files : would it be redundant to go through the loop of filtered stuff like all csv files
    #cleaning the competency column 
    #column_labels = ['Sl.No','Questions','Competency']

    compdf.columns = ['Sl.No', 'Questions', 'Competency']
    
    
    drop_index = compdf.index[(compdf['Questions']== 'Questions') & (compdf['Competency']== 'Competency')]
    if not drop_index.empty:
        drop_index_value = drop_index[0]  # Get the first occurrence index
        compdf = compdf.iloc[drop_index_value + 1:]  # Select all rows after this index
    #compdf.columns = compdf.iloc[1]
    #compdf = compdf[drop_index:]

    print("COMPDF AFTER CLEANING:",compdf)

    #joining the 2 tables
    df_melt = df.melt(id_vars=['State', 'District', 'Block', 'Cluster', 'GPName', 'GP Id',
       'SchoolName', 'SchoolId', 'DiseCode', 'QuestionGroup Id',
       'QuestionGroupName', 'Source Name', 'Date of Visit',
       'Academic Year of Visit', 'Group Value','RespondentType', 'UserType',
       'UserMobileNumber', 'Grade', 'Gender','name_identifier'], var_name='Questions', value_name='Response')
    print("MELTED ORIG DATAFRAME",df_melt)

    merged_df = pd.merge(df_melt,
                     compdf,
                     how='inner',
                     left_on='Questions',
                     right_on='Questions')


    '''merged_df = pd.merge(df.melt(id_vars=['State', 'District', 'Block', 'Cluster', 'GPName', 'GP Id',
       'SchoolName', 'SchoolId', 'DiseCode', 'QuestionGroup Id',
       'QuestionGroupName', 'Source Name', 'Date of Visit',
       'Academic Year of Visit', 'RespondentType', 'UserType',
       'UserMobileNumber', 'Grade', 'Gender'], var_name='Questions', value_name='Response'),
                     compdf,
                     how='inner',
                     left_on='Questions',
                     right_on='Questions')'''
    print("MERGED DF:",merged_df)
    correct_responses = merged_df[merged_df['Response'] == 1]
    question_count = correct_responses.groupby(['District', 'Block','Gender', 'Competency','Questions'])['name_identifier'].nunique().reset_index(name='Correct Question Count')

    total_questions_per_competency = merged_df.groupby('Competency')['Questions'].nunique().reset_index(name='Total Questions')
    overall_compcount = question_count.groupby(['District', 'Block','Gender','Competency'])['Correct Question Count'].sum().reset_index()

    merged_competency_data = pd.merge(overall_compcount, total_questions_per_competency, how='inner', on='Competency')
    #merged_competency_data['Normalized Percentage'] = (merged_competency_data['Correct Count'] / merged_competency_data['Total Questions'] * ) * 100
    
    gen_count = merged_df.groupby(['District','Block','Gender'])['name_identifier'].nunique().reset_index(name='Total Count')

# Step 6: Merge normalized competency data with total count of kids
    final_merged_data = pd.merge(merged_competency_data, gen_count, how='inner', on=['District', 'Block', 'Gender'])
    final_merged_data['Percentage'] = (final_merged_data['Correct Question Count']/(final_merged_data['Total Questions'] * final_merged_data['Total Count'])) * 100

    print("COMPETENCY PERCENTAGE CALCULATION:",final_merged_data)

    # Ensure the directory for heatmaps exists
    output_folder = r'competency_heatmaps/'
    full_output_path = os.path.join(dir_name, output_folder)
    os.makedirs(full_output_path, exist_ok=True)

    # Iterate through each district to create a separate tally table for each
    districts = final_merged_data['District'].unique()
    for district in districts:
        district_data = final_merged_data[final_merged_data['District'] == district]

        # Create the tally table by pivoting the data for the current district
        tally_table = district_data.pivot_table(index=['District', 'Block'], 
                                                columns=['Gender', 'Competency'], 
                                                values='Correct Question Count', 
                                                aggfunc='sum', 
                                                fill_value=0).reset_index()

        # Add total counts for boys and girls and the total population
        tally_table['Total Boys'] = tally_table.filter(like='male').sum(axis=1)
        tally_table['Total Girls'] = tally_table.filter(like='female').sum(axis=1)
        tally_table['Total Population'] = tally_table['Total Boys'] + tally_table['Total Girls']

        # Save the tally table with the district name in the filename
        tally_filename = os.path.join(full_output_path, f'{grade}_competency_tally_table_{district}.csv')
        tally_table.to_csv(tally_filename, index=False)
        print(f"Tally table saved successfully for {district} as: {tally_filename}")

    # (The remaining heatmap plotting code remains unchanged)
    print("All district tally tables saved successfully.")
    math_terms = {
    "Number Sense": "ಸಂಖ್ಯಾ ಜ್ಞಾನ",
    "Place Value": "ಸ್ಥಾನ ಬೆಲೆ",
    "Addition": "ಸಂಕಲನ",
    "Subtraction": "ವ್ಯವಕಲನ",
    "Multiplication": "ಗುಣಾಕಾರ",
    "Division": "ಭಾಗಾಕಾರ",
    "Measurement": "ಅಳತೆಗಳು",
    "Shapes": "ಆಕಾರಗಳು",
    "Data Handling": "ದತ್ತಾಂಶ ನಿರ್ವಹಣೆ",
    "Mensuration": "ಕ್ಷೇತ್ರ ಗಣಿತ"}

    final_merged_data['Block_Kannada'] = final_merged_data['Block'].map(english_to_kannada)
    final_merged_data['Competency_Kannada'] = final_merged_data['Competency'].map(math_terms)


    # Function to plot and save heatmaps
    def plot_heatmap(pivot_counts, pivot_percentages, pivot_annotations, title, filename):
        if pivot_counts.empty or pivot_percentages.empty:
            print(f"No data for {title}. Skipping plot.")
            return

        plt.figure(figsize=(12, 10))  # Increase the figure size
        
        heatmap = sns.heatmap(pivot_percentages, cmap='RdYlGn', annot=pivot_annotations, fmt='', cbar=True, annot_kws={"size": 10, "color": '#4D4D4D'}, vmin=0, vmax=100)  # Adjust font size and scale
        # Set colorbar label color
        colorbar = heatmap.collections[0].colorbar
        colorbar.ax.yaxis.set_tick_params(color='#4E4D4D')  # Dark grey color for colorbar labels
        colorbar.set_label('Percentage', color='#4E4D4D') 
        # Customize plot
        plt.title(title.title(), color='#4E4D4D')
        
        # Set axis labels to dark grey
        plt.xlabel('Block', fontsize=12, color='#4E4D4D')
        plt.ylabel('Competency', fontsize=12, color='#4E4D4D')
        
        # Customize tick labels to dark grey
        plt.xticks(rotation=45, color='#4E4D4D')  # Rotate x-axis labels for better readability
        plt.yticks(rotation=0, color='#4E4D4D')   # Keep y-axis labels horizontal
        plt.tight_layout()
        plt.savefig(filename,format= 'png')
        plt.close()

        # Iterate through each district
    districts = final_merged_data['District'].unique()
    for district in districts:
        # Filter data for the current district
        district_data = final_merged_data[final_merged_data['District'] == district]
        
        # Iterate through genders
        for gender in ['male', 'female']:
            gender_data = district_data[district_data['Gender'] == gender]
            
            # Pivot the data to create a matrix format for heatmap
            pivot_counts = gender_data.pivot(index='Competency', columns='Block', values='Correct Question Count')
            pivot_percentages = gender_data.pivot(index='Competency', columns='Block', values='Percentage')

            #kannada
            pivot_counts_kn = gender_data.pivot(index='Competency_Kannada', columns='Block_Kannada', values='Correct Question Count')
            pivot_percentages_kn = gender_data.pivot(index='Competency_Kannada', columns='Block_Kannada', values='Percentage')
            
            # Ensure no NaN values in the pivot data
            pivot_counts = pivot_counts.fillna(0)
            pivot_percentages = pivot_percentages.fillna(0)
            
            # Create annotations for the heatmap
            pivot_annotations = pivot_counts.astype(int).astype(str) + '\n' + pivot_percentages.round(2).astype(str) + '%'
            
            # Update x-axis labels with block total counts
            block_totals = gender_data[['Block', 'Total Count']].drop_duplicates().set_index('Block')['Total Count']
            updated_columns = [f'{block}\n(Total: {int(count)})' for block, count in block_totals.items()]
            pivot_counts.columns = updated_columns
            pivot_percentages.columns = updated_columns
            pivot_annotations.columns = updated_columns
            
            # Inspect pivot data
            print(f"District: {district}, Gender: {gender}")
            print("Counts:\n", pivot_counts)
            print("Percentages:\n", pivot_percentages)
            print("Annotations:\n", pivot_annotations)
            
            # Plot and save heatmap
            total_responses = block_totals.sum()
            filename = os.path.join(full_output_path, f'{grade}_competency_{district}_heatmap_{gender.lower()}.png')
            plot_heatmap(pivot_counts, pivot_percentages, pivot_annotations, f'{gender.capitalize()} Competency by Block - District: {district} (Total: {total_responses})', filename)

    print("Heatmaps saved successfully.")
    #kannada graphing

    def plot_heatmap_plotly_express(pivot_percentages, pivot_counts, title, filename_kn):
        if pivot_percentages.empty or pivot_counts.empty:
            print(f"No data for {title}. Skipping plot.")
            return

        # Melt the dataframes to long format
        melted_percentages = pivot_percentages.reset_index().melt(id_vars='Competency_Kannada', var_name='Block_Kannada', value_name='Percentage')
        melted_counts = pivot_counts.reset_index().melt(id_vars='Competency_Kannada', var_name='Block_Kannada', value_name='Count')

        # Merge the melted dataframes
        melted_data = pd.merge(melted_percentages, melted_counts, on=['Competency_Kannada', 'Block_Kannada'])

        # Create heatmap
        fig = px.imshow(pivot_percentages,
                        labels=dict(x="Block_Kannada", y="Competency_Kannada", color="ಪ್ರತಿಶತ"),
                        x=pivot_percentages.columns,
                        y=pivot_percentages.index,
                        color_continuous_scale='RdYlGn',
                        range_color=[0, 100],
                        aspect="auto")

        # Add count and percentage as text annotations
        annotations = []
        for _, row in melted_data.iterrows():
            annotations.append(dict(
                x=row['Block_Kannada'],
                y=row['Competency_Kannada'],
                text=f"{int(row['Count'])}<br>{row['Percentage']:.2f}%",
                showarrow=False,
                font=dict(color='black', size=10)
            ))
        fig.update_layout(annotations=annotations)

        # Update layout
        fig.update_layout(
            title=dict(text=title.title(), font=dict(color='#4E4D4D')),
            xaxis=dict(title='ಬ್ಲಾಕ್', tickangle=45, side='bottom'),
            yaxis=dict(title='ಸಾಮರ್ಥ್ಯ'),
            height=800,
            width=1000,
             coloraxis_colorbar=dict(
            title="ಪ್ರತಿಶತ",  # Kannada label
            title_side="right",  # Ensure the title is on the right side of the colorbar
            title_font=dict(size=12),
            tickfont=dict(family='Noto Sans Kannada, Tunga, sans-serif',size=10),
            xpad=20  # Add padding (gap) between the label and the color legend
            )
        )

        # Save the figure
        fig.write_image(filename_kn,scale = 2)
        print(f"Heatmap saved: {filename_kn}")
    
    districts = final_merged_data['District'].unique()
    for district in districts:
        district_data = final_merged_data[final_merged_data['District'] == district]
        
        for gender in ['male', 'female']:
            gender_data = district_data[district_data['Gender'] == gender]

            print("KANNADA UNIQUE COMPETENCY",gender_data['Competency_Kannada'].unique())
            
            # Pivot the data
            pivot_counts = pd.pivot_table(gender_data, values='Correct Question Count', 
                                        index='Competency_Kannada', columns='Block_Kannada', 
                                        aggfunc='sum', fill_value=0)
            pivot_percentages = pd.pivot_table(gender_data, values='Percentage', 
                                            index='Competency_Kannada', columns='Block_Kannada', 
                                            aggfunc='mean', fill_value=0)
            
            # Print pivot tables for verification
            print("KANNADA PIVOT COUNTS:",pivot_counts)
            print("KANNADA PIVOT PERCENTAGE:",pivot_percentages)
            
            # Update column labels with total counts
            block_totals = gender_data.groupby('Block_Kannada')['Total Count'].first()
            updated_columns = [f'{block}\n(ಒಟ್ಟು: {int(count)})' for block, count in block_totals.items()]
            pivot_counts.columns = updated_columns
            pivot_percentages.columns = updated_columns
            
            # Plot and save heatmap
            total_responses = block_totals.sum()
            filename_kn = os.path.join(full_output_path, f'{grade}_competency_{district}_heatmap_{gender.lower()}_kn.png')
            plot_heatmap_plotly_express(pivot_percentages, pivot_counts, 
                                    f'{gender.capitalize()} Competency by Block - District: {district} (Total: {total_responses})', 
                                    filename_kn)

    print("Plotly heatmaps saved successfully.")

    

    
