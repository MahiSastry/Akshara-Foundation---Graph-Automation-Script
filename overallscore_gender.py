import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from kannada_transl import english_to_kannada
import plotly
import plotly.express as px

def score_bracket(total_score):
    if (total_score/20) * 100 >= 0 and (total_score/20) * 100 < 40:
        return "0-40%"
    elif (total_score/20) * 100 >= 40 and (total_score/20) * 100 < 70:
        return "40-70%"
    else:
        return "70-100%"

def score_gender(df,grade,dir_name):
    df['Score Bracket'] = df['Total Score of the Child'].apply(score_bracket)
    genscoredf = df.groupby(['District', 'Block', 'Gender', 'Score Bracket'])['name_identifier'].nunique().reset_index(name='Count')
    print(genscoredf)

    # Specify the folder to save graphs
    output_folder = r'genscore_graphs/'
    full_output_path = os.path.join(dir_name, output_folder)

    # Create the output folder if it doesn't exist
    os.makedirs(full_output_path, exist_ok=True)

    # Iterate through each district to create a tally table and save the CSV
    for district_name, district_data in genscoredf.groupby('District'):
        
        # Create pivot table for each district
        tally_table = district_data.pivot_table(index=['Block'], 
                                                columns=['Gender', 'Score Bracket'], 
                                                values='Count', 
                                                aggfunc='sum', 
                                                fill_value=0).reset_index()

        # Calculate the total population for boys and girls
        tally_table['Total Boys'] = (
            tally_table[('male', '0-40%')] +
            tally_table[('male', '40-70%')] +
            tally_table[('male', '70-100%')]
        )
        tally_table['Total Girls'] = (
            tally_table[('female', '0-40%')] +
            tally_table[('female', '40-70%')] +
            tally_table[('female', '70-100%')]
        )
        tally_table['Total Population'] = tally_table['Total Boys'] + tally_table['Total Girls']

        # Calculate boys and girls who scored >= 40%
        tally_table['Boys >= 40%'] = (
            tally_table[('male', '40-70%')] +
            tally_table[('male', '70-100%')]
        )
        tally_table['Girls >= 40%'] = (
            tally_table[('female', '40-70%')] +
            tally_table[('female', '70-100%')]
        )

        # Save the tally table for each district
        tally_filename = os.path.join(full_output_path, f'{grade}_overallscoregender_tally_table_{district_name}.csv')
        tally_table.to_csv(tally_filename, index=False)
        print(f"Tally table for {district_name} saved successfully as:", tally_filename)

    custom_palette = {'0-40%': '#C7D9BB', '40-70%': '#9CBC87','70-100%':'#72A054'}

    # Iterate through each district
    districts = genscoredf['District'].unique()
    genders = genscoredf['Gender'].unique()

    for district in districts:
        # Filter data for the current district
        for gender in genders:
            district_data = genscoredf[(genscoredf['District'] == district) & (genscoredf['Gender']== gender)]
            
            plt.figure(figsize=(12, 8))
            ax = sns.barplot(
                data=district_data,
                x="Block", y="Count", hue="Score Bracket",
                palette=custom_palette)
            
            # Customize plot
            plt.xlabel("Block", fontsize=12, color='#4E4D4D')
            plt.ylabel("Number of Children", fontsize=12, color='#4E4D4D')
            plt.title(f"District : {district}")

            for p in ax.patches:
                height = p.get_height()
                print(f'Bar height: {height}')  # Debugging print to check the height of each bar
                if height > 1e-6:  # Check if the height is greater than a very small threshold
                    ax.annotate(f'{int(height)}',  # Get height directly from bar
                                (p.get_x() + p.get_width() / 2., height), 
                                
                                ha='center', va='baseline', 
                                fontsize=8, color='#4E4D4D', xytext=(0, 5),
                                textcoords='offset points')
            
            #ax.set_xticklabels([label.get_text().title() for label in ax.get_xticklabels()], rotation=45, color='#4D4D4D')
            # Customize tick labels to dark grey
            plt.xticks(rotation=45, color='#4E4D4D')
            plt.yticks(color='#4E4D4D')
            leg = ax.legend(title='Score Bracket')
            for text in leg.get_texts():
                text.set_color('#4E4D4D')  # Dark grey for legend labels
            leg.get_title().set_color('#4E4D4D')  # Dark grey for legend title
                
            # Add a main title for the entire plot
            #plt.subplots_adjust(top=0.9)
            #g.fig.suptitle(f'District: {district}, Gender : {gender}')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            leg = plt.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.30), frameon=False)

            # Change the color of the legend text
            for text in leg.get_texts():
                text.set_color('#4E4D4D')  # Set your desired color here

            # Optionally, change the legend title color if you have one
            leg.get_title().set_color('#4E4D4D')

            plt.tight_layout()
            #rect=[0, 0, 0.85, 1]
            
            # Save the plot as a PNG file in the output folder
            filename = os.path.join(full_output_path, f'{grade}_genscore_{district}_{gender.lower()}_graph.png')
            plt.savefig(filename, format='png', bbox_inches='tight')
            
            # Close the plot to release memory
            plt.close()

    print("English Graphs saved successfully.")

    # Plot in Kannada
    df['Block_Kannada'] = df['Block'].map(english_to_kannada)
    score_kannada = df.groupby(['District', 'Block','Block_Kannada', 'Gender','Score Bracket'])['name_identifier'].nunique().reset_index(name='Count')
    color_map = {
    '0-40%': '#C7D9BB', '40-70%': '#9CBC87','70-100%':'#72A054'
    }
    for gender in df['Gender'].unique():
        # Filter the data for the current gender
        gender_data = score_kannada[score_kannada['Gender'] == gender]
        
        # Create a bar plot for the current gender
        fig = px.bar(
            gender_data, 
            x='Block_Kannada', 
            y='Count', 
            color='Score Bracket', 
            barmode='group', 
            text='Count', 
            color_discrete_map=color_map
        )
        
        # Customize layout and appearance
        fig.update_layout(
        width=1000,
        height=600,
        xaxis_title='ಬ್ಲಾಕ್',  # Block in Kannada
        yaxis_title='ವಿದ್ಯಾರ್ಥಿಗಳ ಸಂಖ್ಯೆ',  # Number of students in Kannada
        title=f'ಬ್ಲಾಕ್ ಮತ್ತು ಲಿಂಗ ಪ್ರಕಾರದ ಗುರುತಿನ ಸಂಖ್ಯೆಗಳು - {gender}',  # Title including gender
        plot_bgcolor='white',   # White background for the plot area
        paper_bgcolor='white',
        font=dict(              # Set the font to Kannada-compatible font
            family='Noto Sans Kannada, Tunga, sans-serif',
            size=14,
            color='black'
            )
                )
        fig.update_layout(
        xaxis=dict(
            showline=True,       # Show x-axis line
            linecolor='black',   # Color of the x-axis line
            showgrid=False       # Hide x-axis grid lines
        ),
        yaxis=dict(
            showline=True,       # Show y-axis line
            linecolor='black',   # Color of the y-axis line
            showgrid=False       # Hide y-axis grid lines
        )
        )
    
    # Update x-axis for Kannada font
        fig.update_xaxes(
            tickfont=dict(
                family='Noto Sans Kannada, Tunga, sans-serif',  # Kannada font
                size=12,
                color='black'
            )
        )
        
        # Update traces for text display
        fig.update_traces(
            texttemplate='%{text:.}',  # Text template for counts
            textposition='outside'
        )
        # Save the plot as a PNG file with a unique filename based on the gender
        output_filename = os.path.join(full_output_path, f'{grade}_genscore_{district}_{gender.lower()}_graph_kn.png')
        fig.write_image(output_filename, scale=2)  # scale=2 for higher resolution

        print(f"Plot saved as {output_filename}")

    print("Kannada Graphs saved successfully.")