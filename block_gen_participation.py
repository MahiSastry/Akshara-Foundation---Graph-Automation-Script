import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
import plotly.express as px
import kaleido
print(plotly.__version__, kaleido.__version__)
from kannada_transl import english_to_kannada

def blockwise_gen_participate(df,grade,dir_name):
    grouped_data_gender = df.groupby(['District', 'Block', 'Gender'])['name_identifier'].nunique().reset_index(name='Count')

    # output folder to save graphs
    output_folder = r'participation_graphs/'
    full_output_path = os.path.join(dir_name, output_folder)
    # create one if it doesn't exist
    os.makedirs(full_output_path, exist_ok=True)

    # iterate through the district , create tally tables for count verification
    for district_name, district_data in grouped_data_gender.groupby('District'):
        tally_table = district_data.pivot_table(index=['Block'], 
                                                columns=['Gender'], 
                                                values='Count', 
                                                aggfunc='sum', 
                                                fill_value=0).reset_index()

        tally_table.rename(columns={'male': 'Total Boys', 'female': 'Total Girls'}, inplace=True)

        tally_table['Total Population'] = tally_table['Total Boys'] + tally_table['Total Girls']

        tally_filename = os.path.join(full_output_path, f'{grade}_participation_tally_table_{district_name}.csv')
        tally_table.to_csv(tally_filename, index=False)
        print(f"Tally table for {district_name} saved successfully as:", tally_filename)
    custom_palette = {'male': '#AAC698', 'female': '#72A054'}

    # graphing section - english
    districts = grouped_data_gender['District'].unique()
    for district in districts:
        # Filter data for the current district
        district_data = grouped_data_gender[grouped_data_gender['District'] == district]
        fig, ax = plt.subplots()
        sns.barplot(data=district_data, x='Block', y='Count', hue='Gender', ax=ax, palette=custom_palette, legend= False)
        ax.set_title(f'District: {district.title()}', color='#4D4D4D')
    
        # customize axis labels
        ax.set_xlabel('Block', fontsize=12, color='#4E4D4D')
        ax.set_ylabel('Number of Children', fontsize=12, color='#4E4D4D')

        
        #size of the bars and making sure they don't crowd the graphs - for aesthetic purposes
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
        
        # setting tick labels to dark grey
        ax.tick_params(axis='x', rotation=45, colors='#4E4D4D') 
        ax.tick_params(axis='y', colors='#4E4D4D') 

        
        #plt.tight_layout()

        # change legend text to dark grey
        '''leg = ax.legend(title='Gender')
        for text in leg.get_texts():
            text.set_color('#4E4D4D')  # Dark grey for legend labels
        leg.get_title().set_color('#4E4D4D')  # Dark grey for legend title'''

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        #plt.legend(loc='upper right', bbox_to_anchor=(1.5, 1))
        #plt.subplots_adjust(right=0.75)
        leg = plt.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.30), frameon=False)

            # Change the color of the legend text
        for text in leg.get_texts():
            text.set_color('#4E4D4D')  # Set your desired color here

            # Optionally, change the legend title color if you have one
        leg.get_title().set_color('#4E4D4D')


        plt.tight_layout()
        # Save the plot as a PNG file in the output folder
        filename = os.path.join(full_output_path, f'{grade}participation_{district}_graph.png')
        plt.savefig(filename, format = 'png')
        
        # Close the plot to release memory
        plt.close()

    print("English Graphs saved successfully.")

    #Kannada
    df['Block_Kannada'] = df['Block'].map(english_to_kannada)
    grouped_kannada = df.groupby(['District', 'Block','Block_Kannada', 'Gender'])['name_identifier'].nunique().reset_index(name='Count')
    color_map = {
        'male': '#AAC698', 'female': '#72A054'
    }

    fig = px.bar(grouped_kannada, x = 'Block_Kannada', y = 'Count', color = 'Gender',barmode = 'group', text='Count',color_discrete_map=color_map)
    fig.update_layout(
        width=1000,
        height=600,
        xaxis_title='ಬ್ಲಾಕ್',  # block in Kannada
        yaxis_title='ವಿದ್ಯಾರ್ಥಿಗಳ ಸಂಖ್ಯೆ',  # number of students in Kannada
        title=f'District: {district.title()}',  
        plot_bgcolor='white',   
        paper_bgcolor='white',
        #xaxis=dict(showgrid=True, gridcolor='black'),  
        #yaxis=dict(showgrid=True, gridcolor='black')   
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

    #  update x-axis to make text bold
    fig.update_xaxes(
        tickfont=dict(
            family='Arial Bold, sans-serif',
            size=12,
            color='black'
        )
    )

    
    fig.update_traces(
        texttemplate='%{text:.}',
        textposition='outside'
    )

    # Show the plot
    #fig.show()
    '''fig.write_image("kannada_plot.png", width=1000,
        height=600,scale=1)  # scale=2 for higher resolution'''
    filename_kn = os.path.join(full_output_path, f'{grade}participation_{district}_graph_kn.png')
    fig.write_image(filename_kn, scale=2)

    print("Kannada graphs saved successfully")
