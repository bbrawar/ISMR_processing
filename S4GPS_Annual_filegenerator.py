import numpy as np
import pandas as pd
import glob
import tkinter as tk
from tkinter import filedialog
import datetime
from alive_progress import alive_bar

# Function to map PRN to satellite identifier
def PRN_X(x):
    # Map PRN to satellite identifier based on ranges
    if 0 < x < 38:
        sv = 'G' + str(x)  # GPS satellites
    elif 37 < x < 62:
        sv = 'R' + str(x)  # GLONASS satellites
    elif 70 < x < 107:
        x = str(x)[-2:] if len(str(x)) > 2 else str(x)
        sv = 'E' + x  # Galileo satellites
    elif 119 < x < 139:
        x = str(x)[-2:] if len(str(x)) > 2 else str(x)
        sv = 'S' + x  # SBAS satellites
    elif 140 < x < 177:
        x = str(x)[-2:] if len(str(x)) > 2 else str(x)
        sv = 'C' + x  # BeiDou satellites
    elif 181 < x < 187:
        x = str(x)[-2:] if len(str(x)) > 2 else str(x)
        sv = 'J' + x  # QZSS satellites
    else:
        sv = 'M' + str(x)  # Other satellites (e.g., MEO, IRNSS, etc.)
    return sv

# Function to convert GPS week and time of week to datetime
def WN_TOWtoTIME(WN, TOW):
    WN, TOW = float(WN), float(TOW)
    leapseconds = 0  # Placeholder for leap seconds (needs to be updated)
    datetimeformat = "%Y-%m-%d %H:%M:%S"
    epoch = datetime.datetime.strptime("1980-01-06 00:00:00", datetimeformat)
    elapsed = datetime.timedelta(days=(WN * 7), seconds=TOW)
    return elapsed + epoch

def correctdS4(S4,noiseS4):
    temp = S4**2-noiseS4**2
    if temp > 0:
        return temp**(0.5)
    else:
        return 0

# Initialize the Tkinter interface to select a directory
root = tk.Tk()
root.withdraw()
file_path = filedialog.askdirectory()

# Create a list of ISMR files in the selected directory
path = file_path + '/*.ismr'
files = glob.glob(path)

# Initialize a progress bar
with alive_bar(len(files), force_tty=True) as bar:
    # Initialize an empty DataFrame to store scintillation data
    scinti_year = pd.DataFrame()
    
    # Loop through each ISMR file
    for day_file in files:
        year = int(file_path[-4:])
        DAY_OF_YEAR = int(day_file[-8:-5])
        print(str(DAY_OF_YEAR)+"/n===============")
        d = datetime.date(year, 1, 1) + datetime.timedelta(DAY_OF_YEAR - 1)
        
        # Read ISMR data from the file into a DataFrame
        data = pd.read_csv(day_file, header=None)
        # Assign meaningful column names (you can fill in the actual column names)
        data.columns = ['WN','TOW','SVID', 'Value', 'Azimuth', 'Elevation', 'Sig1', 'Total_S4_Sig1',
               'Correction_total_S4_Sig1', 'Phi01_Sig1_1', 'Phi03_Sig1_3',
               'Phi10_Sig1_10', 'Phi30_Sig1_30', 'Phi60_Sig1_60',
               'AvgCCD_Sig1_average_code-carrier_divergence',
               'SigmaCCD_Sig1_standard_deviation_code-carrier_divergence',
               'TEC_TOW-45s', 'dTEC_TOW-60s_TOW-45s', 'TEC_TOW-30s',
               'dTEC_TOW-45s_TOW-30s', 'TEC_TOW-15s', 'dTEC_TOW-30s_TOW-15s',
               'TEC_TOW', 'dTEC_TOW-15s_TOW', 'Sig1_lock_time',
               'sbf2ismr_version_number', 'Lock_time_second_frequency_TEC',
               'Averaged_C/N0_second_frequency_TEC_computation', 'SI_Index_Sig1',
               'SI_Index_Sig1_numerator', 'p_Sig1_spectral_slope', 'Average_Sig2_C/N0',
               'Total_S4_Sig2', 'Correction_total_S4_Sig2', 'Phi01_Sig2_1',
               'Phi03_Sig2_3', 'Phi10_Sig2_10', 'Phi30_Sig2_30', 'Phi60_Sig2_60',
               'AvgCCD_Sig2_average_code-carrier_divergence', 'SigmaCCD_Sig2_standard',
               'Sig2_lock', 'SI_Index_Sig2', 'SI_Index_Sig2_numerator', 'p_Sig2_phase',
               'Average_Sig3_C/N0_last_minute', 'Total_S4_Sig3',
               'Correction_total_S4_Sig3', 'Phi01_Sig3_1_phase', 'Phi03_Sig3_3_phase',
               'Phi10_Sig3_10_phase', 'Phi30_Sig3_30_phase', 'Phi60_Sig3_60_phase',
               'AvgCCD_Sig3_average_code-carrier_divergence',
               'SigmaCCD_Sig3_standard_deviation_code-carrier_divergence',
               'Sig3_lock_time', 'SI_Index_Sig3', 'SI_Index_Sig3_numerator',
               'p_Sig3_phase', 'T_Sig1_phase', 'T_Sig2_phase', 'T_Sig3_phase']

        # Apply the PRN_X function to create an 'sv' column with satellite identifiers
        data['sv'] = data.SVID.apply(PRN_X)
        # Convert GPS week and time of week to UTC and local time
        data['DateTime_UTC'] = np.vectorize(WN_TOWtoTIME)(data['WN'], data['TOW'])
        data['DateTime_IST'] = data.DateTime_UTC + datetime.timedelta(hours=5.5)
        
        # Extract various time-related attributes
        data['JT'] = pd.DatetimeIndex(data['DateTime_UTC']).floor('d').to_julian_date()
        data['Dates'] = pd.to_datetime(data['DateTime_IST']).dt.date
        data['Time_LT'] = pd.to_datetime(data['DateTime_IST']).dt.time
        data['Time_UT'] = pd.to_datetime(data['DateTime_UTC']).dt.time
        
        # Filter data based on elevation cutoff
        data = data[data['Elevation'].astype(float) >= 35]
        
        # Assuming correctdS4 is defined somewhere
        data['S4cor'] = np.vectorize(correctdS4)(
            data['Total_S4_Sig1'].astype(float),
            data['Correction_total_S4_Sig1'].astype(float)
        )
        
        # Further filter data based on S4cor
        data = data[data['S4cor'] <= 1.4]
        
        # Categorize data based on satellite system
        data_gps = data.loc[data['SVID'].between(1, 37, inclusive="both")]
        #data_glonass = data.loc[data['SVID'].between(38, 61, inclusive="both")]
        # ... (other categorizations)
        
        # Extract relevant columns for the scinti_day DataFrame
        scinti_day = data_gps[['DateTime_UTC', 'DateTime_IST', 'Dates', 'Time_LT', 'Total_S4_Sig1', 'S4cor']]
        # Append the daily scintillation data to the yearly DataFrame
        #scinti_year = scinti_year.append(scinti_day, ignore_index=True)
        scinti_year = pd.concat([scinti_year, scinti_day], ignore_index=True)
        # Update the progress bar
        bar()
    
    # Save the yearly scintillation data to a CSV file
    scinti_year.to_csv(f'{year}/scinti_S4cGPS{year}.csv')
