import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns
import numpy as np

st.title('MLB Swing Speed App')
st.write('Find me [@Blandalytics](https://twitter.com/blandalytics) and check out the data at [Baseball Savant](https://baseballsavant.mlb.com/leaderboard/bat-tracking)')

pl_white = '#FEFEFE'
pl_background = '#162B50'
pl_text = '#72a3f7'
pl_line_color = '#293a6b'

sns.set_theme(
    style={
        'axes.edgecolor': pl_line_color,
        'axes.facecolor': pl_background,
        'axes.labelcolor': pl_white,
        'xtick.color': pl_white,
        'ytick.color': pl_white,
        'figure.facecolor':pl_background,
        'grid.color': pl_background,
        'grid.linestyle': '-',
        'legend.facecolor':pl_background,
        'text.color': pl_white
     }
    )

all_swings = st.toggle('Include Non-Competitive swings?')

swing_data = pd.read_csv('https://github.com/Blandalytics/baseball_snippets/blob/main/swing_speed_data.csv?raw=true',encoding='latin1')
if all_swings==False:
    swing_data = swing_data.loc[(swing_data['bat_speed']>=40) &
                                (swing_data['bat_speed']>swing_data['bat_speed'].groupby(swing_data['Hitter']).transform(lambda x: x.quantile(0.1)))].copy()
swing_data['squared_up_frac'] = swing_data['squared_up_frac'].mul(100)
swing_data['swing_time'] = swing_data['swing_time'].mul(1000)
swing_data['game_date'] = pd.to_datetime(swing_data['game_date'])

col1, col2 = st.columns(2)

with col1:
    swing_threshold = st.number_input(f'Min # of Swings:',
                                      min_value=0, 
                                      max_value=swing_data.groupby('Hitter')['Swings'].sum().max(),
                                      step=25, 
                                      value=100)
with col2:
    team = st.selectbox('Team:',
                        ['All','ATL', 'AZ', 'BAL', 'BOS', 'CHC', 'CIN', 'CLE', 'COL', 'CWS',
                         'DET', 'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM',
                         'NYY', 'OAK', 'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX',
                         'TOR', 'WSH'])

stat_name_dict = {
    'bat_speed':'Swing Speed (mph)',
    'swing_length':'Swing Length (ft)',
    'swing_time':'Swing Time (ms)',
    'swing_acceleration':'Swing Acceleration (ft/s^2)',
    'squared_up_frac':'Squared Up%'
}

df_stat_dict = {
    'bat_speed':'Speed (mph)',
    'swing_length':'Length (ft)',
    'swing_time':'Time (ms)',
    'swing_acceleration':'Acceleration (ft/s^2)',
    'squared_up_frac':'SU%'
}

st.write('Swing Metrics')
st.dataframe((swing_data if team=='All' else swing_data.loc[swing_data['Team']==team])
             .groupby(['Hitter'])
             [['Team','Swings','bat_speed','swing_length','swing_time','swing_acceleration','squared_up_frac']]
             .agg({
                 'Team':lambda x: pd.Series.unique(x)[-1],
                 'Swings':'count',
                 'bat_speed':'mean',
                 'swing_length':'mean',
                 'swing_time':'mean',
                 'swing_acceleration':'mean',
                 'squared_up_frac':'mean'
             })
             .query(f'Swings >={swing_threshold}')
             .sort_values('swing_acceleration',ascending=False)
             .round(1)
             .rename(columns=df_stat_dict)
)

players = list(swing_data
               .groupby('Hitter')
               [['Swings','swing_acceleration']]
               .agg({'Swings':'count','swing_acceleration':'mean'})
               .query(f'Swings >={swing_threshold}')
               .reset_index()
               .sort_values('swing_acceleration', ascending=False)
               ['Hitter']
              )
col1, col2 = st.columns(2)

with col1:
    player = st.selectbox('Choose a player:', players)
with col2:
    stat = st.selectbox('Choose a metric:', list(stat_name_dict.values()), index=2)
    stat = list(stat_name_dict.keys())[list(stat_name_dict.values()).index(stat)]
    players = list(swing_data
               .groupby('Hitter')
               [['Swings',stat]]
               .agg({'Swings':'count',stat:'mean'})
               .query(f'Swings >={swing_threshold}')
               .reset_index()
               .sort_values(stat, ascending=False)
               ['Hitter']
              )

col1, col2 = st.columns(2)
season_start = swing_data.loc[swing_data['Hitter']==player,'game_date'].min()
season_end = swing_data.loc[swing_data['Hitter']==player,'game_date'].max()
with col1:
    start_date = st.date_input(f"Start Date (Season started: {season_start:%b %d})", 
                               season_start,
                               min_value=season_start,
                               max_value=season_end,
                               format="MM/DD/YYYY")
with col2:
    end_date = st.date_input(f"End Date (Season ended: {season_end:%b %d})", 
                             season_end,
                             min_value=season_start,
                             max_value=season_end,
                             format="MM/DD/YYYY")
    
def speed_dist(swing_data,player,stat):
    fig, ax = plt.subplots(figsize=(6,3))
    swing_data = swing_data.loc[(swing_data['game_date'].dt.date>=start_date) &
                                (swing_data['game_date'].dt.date<=end_date)].copy()

    val = swing_data.loc[swing_data['Hitter']==player,stat].mean()
    color_list = sns.color_palette('vlag',n_colors=len(players))
    player_color = color_list[len(players)-players.index(player)-1] if stat not in ['swing_length','swing_time'] else color_list[players.index(player)-1]
    sns.kdeplot(swing_data.loc[swing_data['Hitter']==player,stat],
                    color=player_color,
                    fill=True,
                    cut=0)
                    
    g = sns.kdeplot(swing_data[stat],
                    linestyle='--',
                    color='w',
                    alpha=0.5,
                    cut=0)
    
    league_val = swing_data[stat].mean()
    kdeline_g = g.lines[0]
    xs_g = kdeline_g.get_xdata()
    ys_g = kdeline_g.get_ydata()
    height_g = np.interp(league_val, xs_g, ys_g)
    ax.vlines(league_val, 0, height_g, color='w',alpha=0.5,linestyle='--')

    p = sns.kdeplot(swing_data.loc[swing_data['Hitter']==player,stat],
                    color=player_color,
                    cut=0)
    if all_swings==True:
        xlim = (min(swing_data[stat].quantile(0.01),swing_data.loc[swing_data['Hitter']==player,stat].quantile(0.02)),
                 max(200,swing_data.loc[swing_data['Hitter']==player,stat].quantile(0.99)) if stat == 'swing_time' else swing_data[stat].max())
    else:
        xlim = (ax.get_xlim()[0],ax.get_xlim()[1])
    ax.set(xlim=xlim,
           xlabel=stat_name_dict[stat],
           ylabel='',
          ylim=(0,ax.get_ylim()[1]*1.15))

    plt.legend(labels=[player,'league Avg','MLB'][::2],
               loc='upper center',
               ncol=2,
               edgecolor=pl_background)
    
    kdeline_p = p.lines[1]
    xs_p = kdeline_p.get_xdata()
    ys_p = kdeline_p.get_ydata()
    height_p = np.interp(val, xs_p, ys_p)
    ax.vlines(val, ax.get_ylim()[1]*0.1, height_p, color=player_color)
    
    measure = '%' if stat == 'squared_up_frac' else stat_name_dict[stat].split(' ')[-1][1:-1]
    ax.text(val,ax.get_ylim()[1]*0.1,f'{val:.1f}{measure}',va='center',ha='center',color=player_color,
            bbox=dict(facecolor=pl_background, alpha=0.9,edgecolor=player_color))

    if stat=='squared_up_frac':
        plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(100,decimals=0))
    ax.set_yticks([])
    title_stat = 'Squared Up%' if stat == 'squared_up_frac' else ' '.join(stat_name_dict[stat].split(' ')[:-1])
    apostrophe_text = "'" if player[-1]=='s' else "'s"
    date_text = '' if (start_date==season_start) & (end_date==season_end) else f'\n({start_date:%b %-d} - {end_date:%b %-d})'
    fig.suptitle(f"{player}{apostrophe_text}\n{title_stat} Distribution{date_text}",y=1.025 if date_text=='' else 1.04)
    sns.despine(left=True)
    fig.text(0.8,-0.15,'@blandalytics\nData: Savant',ha='center',fontsize=10)
    fig.text(0.125,-0.14,'mlb-swing-speed.streamlit.app',ha='left',fontsize=10)
    st.pyplot(fig)
speed_dist(swing_data,player,stat)

st.header('Assumptions & Formulas')
st.write('Assumptions:')
st.write('- Initial speed is 0mph')
st.write('- Swing Speed is recorded at the same point & time as Swing Length')
st.write('- Speed of pitch at plate = [~0.92 * Release Speed](https://twitter.com/tangotiger/status/1790432119275082139)')
st.write('- Collision Efficiency = [0.23](http://tangotiger.com/index.php/site/article/statcast-lab-collisions-and-the-perfect-swing)')
st.write("- Squared Up% can't be >100%")
st.write('Formulas:')
st.write('- Initial Speed (v_0; in ft/s) = 0 ')
st.write('- Final Speed (v_f; in ft/s) = Swing Speed * 1.46667 (from Savant; converted from mph to ft/s)')
st.write('- Swing Length (d; in ft) = Swing Length (from Savant)')
st.write('- Average Speed (v_avg; in ft/s) = (v_f - v_i)/2')
st.write('- Swing Time (t; in s) = d / v_avg')
st.write('- Swing Acceleration (a; in ft/s^2) = v_f / t')
st.write('- Collision Efficiency (q; unitless) = 0.23')
st.write('- Max Possible EV (in mph) = (Pitch Speed at Plate * q) + [Swing Speed * (1 + q]')
st.write('- Squared Up% (SU%; % of Max Possible EV) = Exit Velocity / Max Possible EV')
