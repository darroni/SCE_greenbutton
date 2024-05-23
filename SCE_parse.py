# Description: This script parses the data from the SCE usage file and writes it to a new file.

import csv
import datetime
import pandas as pd
import warnings

# Pandas will throw a future warning when injecting unsupport dtypes into a dataframe.  This is intended to suppress that warning.
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define and write the header row to the output file
def print_header(outfile):
    with open(outfile, 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(["Date", "StartTime", "EndTime", "kwHUsage", "Tag", "Season", "Year", "Month", "BillingSeason", "BillingDay", "TOU", "Cost"])

# Parse the data from the input file and write it to the output file
def parse_data(infile, outfile):
    rows_gen = 0
    rows_del = 0
    tag = ''
    
    with open(infile, 'r', newline='') as f_in, open(outfile, 'a', newline='') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        
        # Set the power direction tag (i.e., outgoing/generated or incoming/delivered) 
        # Get the values from the input file that will be written to the output file
        for row in reader:
            if not row:
                continue
            if 'Received' in row[0]:
                tag = 'generated'
            elif 'Delivered' in row[0] or 'Consumption' in row[0]:
                tag = 'delivered'
            elif 'to' in row[0]:
                kwHUsage = float(row[1])
                parse_row = row[0].split('to')
                parse_row = [item.replace('Â\xa0', '') for item in parse_row]
                start = parse_row[0].split(' ')
                date = start[0].strip()
                startTime = start[1].strip()
                end = parse_row[1].split(' ')
                endTime = end[2].strip()

                if kwHUsage != 0:
                    data = [date, startTime, endTime, kwHUsage, tag]
                    writer.writerow(data)
                    if tag == 'generated':
                        rows_gen += 1
                    elif tag == 'delivered':
                        rows_del += 1

# Add the month and year to the output file
def add_month_year(outfile):
    month = {
        "01": "January", "02": "February", "03": "March", "04": "April", "05": "May", 
        "06": "June", "07": "July", "08": "August", "09": "September", "10": "October", 
        "11": "November", "12": "December"
    }
    
    try:
        data = pd.read_csv(outfile)
        data['Month'] = pd.to_datetime(data['Date']).dt.month.map("{:02d}".format).map(month)
        data['Year'] = pd.to_datetime(data['Date']).dt.year
        data.to_csv(outfile, index=False)
    except Exception as e:
        print(f"Error adding month/year: {e}")

# Add the calendar and billing seasons to the output file
def add_seasons(outfile):
    season = {
        "January": "Winter", "February": "Winter", "March": "Winter", "April": "Spring", 
        "May": "Spring", "June": "Spring", "July": "Summer", "August": "Summer", 
        "September": "Summer", "October": "Fall", "November": "Fall", "December": "Fall",
    }
    billing_season = {
        "January": "Winter", "February": "Winter", "March": "Winter", "April": "Winter", 
        "May": "Winter", "June": "Summer", "July": "Summer", "August": "Summer", 
        "September": "Summer", "October": "Winter", "November": "Winter", "December": "Winter",
    }
    
    try:
        data = pd.read_csv(outfile)
        data['Season'] = data['Month'].map(season)
        data['BillingSeason'] = data['Month'].map(billing_season)
        data.to_csv(outfile, index=False)
    except Exception as e:
        print(f"Error adding seasons: {e}")

# Label the day as weekday or weekend and write to the output file
def add_weekday(outfile):
    weekday = {
        0: "Weekend", 1: "Weekday", 2: "Weekday", 3: "Weekday", 4: "Weekday", 
        5: "Weekday", 6: "Weekend",
    }
    
    try:
        data = pd.read_csv(outfile)
        data['BillingDay'] = pd.to_datetime(data['Date']).dt.weekday.map(weekday)
        data.to_csv(outfile, index=False)
    except Exception as e:
        print(f"Error adding weekday: {e}")

# Add the time of use (TOU) to the output file.
# The TOU is based on the time of day, billing season, and billing day.
def add_tou(outfile):
    try:
        data = pd.read_csv(outfile)
        data['TOU'] = 'Off-Peak'
        
        winter_mask = data['BillingSeason'] == 'Winter'
        summer_mask = data['BillingSeason'] == 'Summer'
        weekday_mask = data['BillingDay'] == 'Weekday'
        weekend_mask = data['BillingDay'] == 'Weekend'

        data.loc[winter_mask & (data['StartTime'] >= '21:00:00') & (data['EndTime'] <= '08:00:00'), 'TOU'] = 'Off-Peak'
        data.loc[winter_mask & (data['StartTime'] >= '16:00:00') & (data['EndTime'] <= '21:00:00'), 'TOU'] = 'Mid-Peak'
        data.loc[winter_mask & (data['StartTime'] >= '08:00:00') & (data['EndTime'] <= '16:00:00'), 'TOU'] = 'Super-Off-Peak'
        data.loc[summer_mask & weekend_mask & (data['StartTime'] >= '16:00:00') & (data['EndTime'] <= '21:00:00'), 'TOU'] = 'Mid-Peak'
        data.loc[summer_mask & weekday_mask & (data['StartTime'] >= '16:00:00') & (data['EndTime'] <= '21:00:00'), 'TOU'] = 'On-Peak'
        data.loc[winter_mask & ((data['StartTime'] >= '23:00:00') | (data['StartTime'] < '00:00:00')), 'TOU'] = 'Off-Peak'
        
        data.to_csv(outfile, index=False)
    except Exception as e:
        print(f"Error adding TOU: {e}")

# Add the delivery cost to the output file.
# The delivery cost is based on the billing season, billing day, and TOU.
# It is calculated as the product of the usage and the delivery cost.
# the del_costs dictionary is based on SCE's TOU-D-Prime rate schedule.
def add_delivery_cost(outfile):
    del_costs = {
        ("Winter", "Weekday", "Off-Peak"): 0.24, ("Winter", "Weekday", "Mid-Peak"): 0.6,
        ("Winter", "Weekday", "Super-Off-Peak"): 0.24, ("Winter", "Weekend", "Off-Peak"): 0.24,
        ("Winter", "Weekend", "Mid-Peak"): 0.6, ("Winter", "Weekend", "Super-Off-Peak"): 0.24,
        ("Summer", "Weekday", "Off-Peak"): 0.26, ("Summer", "Weekday", "On-Peak"): 0.63,
        ("Summer", "Weekend", "Mid-Peak"): 0.39, ("Summer", "Weekend", "Off-Peak"): 0.26,
    }
    
    try:
        data = pd.read_csv(outfile)
        data['Cost'] = data.apply(
            lambda row: row['kwHUsage'] * del_costs.get((row['BillingSeason'], row['BillingDay'], row['TOU']), 0), axis=1
        )
        data.to_csv(outfile, index=False)
    except Exception as e:
        print(f"Error adding cost: {e}")

# Add the received value to the output file.
# The received value is based on the generated kwH. SCE's Pacific Time Zone ECC data found at: 
# https://www.sce.com/sites/default/files/custom-files/PDF_Files/EEC_Factors_Nov_2023.xlsx
def add_received_value(outfile):
    try:
        source_df = pd.read_csv(outfile)
        reference_df = pd.read_csv('/users/darroni/OneDrive/Documents/Solar/SCEUsage/ECC_data.csv')
        
        # Manage the time format to support the reference data
        source_df['StartTime'] = pd.to_datetime(source_df['StartTime'], format='%H:%M:%S').dt.hour
        source_df.loc[source_df['StartTime'] == 0, 'StartTime'] = 24

        generated_df = source_df[source_df['Tag'] == 'generated']

        calculated_costs = []
        for _, row in generated_df.iterrows():
            year, month, hour = row['Year'], row['Month'], row['StartTime']
            weekend = row['BillingDay'] == 'Weekend'
            ref_row = reference_df[
                (reference_df['Price Effective Date'] == year) & 
                (reference_df['Month'] == month) & 
                (reference_df['Hour'] == hour)
            ]
            if not ref_row.empty:
                cost = ref_row['SCE Gen - Weekend/Holiday EEC'].values[0] if weekend else ref_row['SCE Gen - Weekday EEC'].values[0]
                calculated_costs.append(row['kwHUsage'] * cost)
            else:
                calculated_costs.append(None)

        generated_df.loc[:, 'Cost'] = calculated_costs
        source_df.update(generated_df['Cost'])

        # Reset the time format to the original
        source_df['StartTime'] = source_df['StartTime'].apply(lambda x: '00:00:00' if x == 24 else datetime.time(x).strftime('%H:%M:%S'))
        source_df.to_csv(outfile, index=False)

        print("Received Value complete")
    except Exception as e:
        print(f"Error adding received value: {e}")

# Consolidate the SBP's 15 minute blocks of time into single hour blocks.
# This reduces the rows in the output file and make it easier to analyze in Excel as a Pivot Table.
def combine_data(outfile):
    try:
        data = pd.read_csv(outfile)
        data['StartTime'] = pd.to_datetime(data['StartTime'], format='%H:%M:%S').dt.time
        data['EndTime'] = pd.to_datetime(data['EndTime'], format='%H:%M:%S').dt.time
        data['Hour'] = pd.to_datetime(data['StartTime'].astype(str), format='%H:%M:%S').dt.hour
        
        agg_dict = {
            'kwHUsage': 'sum',
            'Cost': 'sum',
            'Season': 'first',
            'Year': 'first',
            'Month': 'first',
            'BillingSeason': 'first',
            'BillingDay': 'first',
            'TOU': 'first'
        }
        
        grouped_data = data.groupby(['Date', 'Hour', 'Tag']).agg(agg_dict).reset_index()
        grouped_data['StartTime'] = grouped_data['Hour'].apply(lambda x: f'{x:02}:00:00')
        grouped_data['EndTime'] = grouped_data['Hour'].apply(lambda x: f'{x+1:02}:00:00' if x < 23 else '00:00:00')
        grouped_data = grouped_data.drop(columns=['Hour'])
        
        ordered_columns = ['Date', 'StartTime', 'EndTime', 'kwHUsage', 'Tag', 'Season', 'Year', 'Month', 'BillingSeason', 'BillingDay', 'TOU', 'Cost']
        grouped_data = grouped_data[ordered_columns]
        
        grouped_data.to_csv(outfile, index=False)
    except Exception as e:
        print(f"Error combining data: {e}")

# Main function to run the program
if __name__ == "__main__":
    input_file = "sce_usage.csv"
    output_file = input_file.split('.')[0] + "_parsed.csv"

    print_header(output_file)
    parse_data(input_file, output_file)
    add_month_year(output_file)
    add_seasons(output_file)
    add_weekday(output_file)
    add_tou(output_file)
    add_delivery_cost(output_file)
    add_received_value(output_file)
    combine_data(output_file)

    print("Parsing complete! Output is in " + output_file)
