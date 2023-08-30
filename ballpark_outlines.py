import pandas as pd
import matplotlib.pyplot as plt

# Load stadium dimensions
stadium_df = pd.read_csv('https://raw.githubusercontent.com/jldbc/pybaseball/master/pybaseball/data/mlbstadiums.csv').drop(columns=['Unnamed: 0'])

# Function to plot stadium dimensions
def stadium_plot(team, ax, scale_val_bat, segments=['outfield_outer','foul_lines','infield_inner','infield_outer']):
  stadium_graph_data = stadium_df.loc[stadium_df['team']==team]

  for segment in segments:
    ax.plot(stadium_graph_data.loc[stadium_df['segment']==segment,'x'],
            stadium_graph_data.loc[stadium_df['segment']==segment,'y'],
            linewidth=round(scale_val_bat*1.5), color='black', alpha=0.8)
