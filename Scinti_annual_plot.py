import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import numpy as np
import tkinter as tk
from tkinter import filedialog
import datetime

# User input for the year
year = input('Year = ')

# Read the CSV file into a DataFrame
df = pd.read_csv(f'{year}/scinti_S4c{year}.csv', index_col=0, low_memory=False)

# Convert date and time columns to datetime format
df['DateTime_UTC'] = pd.to_datetime(df['DateTime_UTC'])
df['DateTime_IST'] = pd.to_datetime(df['DateTime_IST'])

# Set DateTime_UTC as the index
df.set_index('DateTime_UTC', inplace=True)

# Convert Total_S4_Sig1 column to float
df['Total_S4_Sig1'] = df['Total_S4_Sig1'].astype(float)

# Filter rows where Total_S4_Sig1 <= 1.25
df = df[df['Total_S4_Sig1'] <= 1.25]

# Calculate maximum S4 value for each DateTime_UTC
df['S4_max'] = df.groupby(['DateTime_UTC'])['Total_S4_Sig1'].transform(max)

# Remove duplicate DateTime_UTC entries, keeping the last occurrence
df = df[~df.index.duplicated(keep='last')]

# Set S4_max values less than 0.3 to NaN
df.loc[df['S4_max'] < 0.3, 'S4_max'] = np.nan

# Create a date range from January 1st to January 1st of the next year with a frequency of 1 minute
idx = pd.date_range(f'01-01-{year}', f'01-01-{int(year)+1}', freq='1min')

# Reindex the DataFrame with the new date range and fill missing values with NaN
df.index = pd.DatetimeIndex(df.index)
df = df.reindex(idx, fill_value=np.nan)

# Add 5.5 hours to the index to convert to IST (Indian Standard Time)
df['DateTime_IST'] = df.index + datetime.timedelta(hours=5.5)



# Pivot the DataFrame to create a heatmap
df_pivot = df.pivot_table(index=df.index.time, columns=df.index.date, values='S4_max', dropna=False)
df_pivot = df_pivot[df_pivot.index >= datetime.time(12, 30, 0)]

# Add 5.5 hours to the index of the pivoted DataFrame to convert to IST
delta = datetime.timedelta(hours=5.5)
datetime_index = pd.to_datetime(df_pivot.index, format='%H:%M:%S')
datetime_index += delta
new_time_index = datetime_index.time
df_pivot.index = new_time_index


# Create a heatmap using seaborn
fig, axes = plt.subplots(figsize=(21, 5))
#fig, axes = plt.subplots()

#plt.xticks(fontsize=14)
#plt.yticks(fontsize=14)



#sns.set(rc={'axes.facecolor': 'white', 'figure.facecolor': 'white'})

sns.set(rc={'axes.linewidth': 2,
            'axes.facecolor': 'white',
            'axes.edgecolor': 'black' ,
            'axes.labelcolor': 'black',
            'text.color': 'black', 
            'xtick.color': 'black', 
            'ytick.color': 'black',
            'xtick.major.width': 2, 
            'ytick.major.width': 2,
            'ytick.minor.width': 1 ,
            'xtick.minor.width': 1 ,
            'xtick.major.size': 10, 
            'ytick.major.size': 10, 
            'xtick.minor.size': 6, 
            'ytick.minor.size': 6,
            'xtick.direction': 'in',
            'ytick.direction': 'in',
            'font.size': 15,
            'legend.fontsize':15,
            'legend.borderaxespad': 1.9, 
            'axes.labelpad': 10  }, 
        style='ticks', 
        context='paper', 
        font_scale=2)


res=sns.heatmap(df_pivot, cmap='jet', cbar_kws={'label': '$S_4$ index'}, vmin=0.3, vmax=1.4)
axes.invert_yaxis()
axes.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

plt.xlabel('Months')
plt.ylabel('LT')
plt.locator_params(axis='x', nbins=12)
plt.locator_params(axis='y',nbins=6.5)
for _, spine in res.spines.items():
    spine.set_visible(True)
    spine.set_linewidth(2)



# Display the plot
#plt.show()

#to save plot
plt.savefig(f'Scinti{year}_sunset2.png',facecolor='white', dpi=500, bbox_inches='tight')
