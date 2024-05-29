# Description: This script parses the data from the SCE usage file and writes it to a new file.

import csv
import datetime
import pandas as pd
import warnings

# Constants
MONTH_MAP = {
    "01": "January", "02": "February", "03": "March", "04": "April", "05": "May",
    "06": "June", "07": "July", "08": "August", "09": "September", "10": "October",
    "11": "November", "12": "December"
}
SEASON_MAP = {
    "January": "Winter", "February": "Winter", "March": "Winter", "April": "Spring",
    "May": "Spring", "June": "Spring", "July": "Summer", "August": "Summer",
    "September": "Summer", "October": "Fall", "November": "Fall", "December": "Fall"
}
# The billing season is based on SCE's TOU-D-Prime Billing Season schedule.
BILLING_SEASON_MAP = {
    "January": "Winter", "February": "Winter", "March": "Winter", "April": "Winter",
    "May": "Winter", "June": "Summer", "July": "Summer", "August": "Summer",
    "September": "Summer", "October": "Winter", "November": "Winter", "December": "Winter"
}
WEEKDAY_MAP = {
    0: "Weekend", 1: "Weekday", 2: "Weekday", 3: "Weekday", 4: "Weekday",
    5: "Weekday", 6: "Weekend"
}
# Delivery costs are based on SCE's TOU-D-Prime rate schedule.
DELIVERY_COSTS = {
    ("Winter", "Weekday", "Off-Peak"): 0.24, ("Winter", "Weekday", "Mid-Peak"): 0.6,
    ("Winter", "Weekday", "Super-Off-Peak"): 0.24, ("Winter", "Weekend", "Off-Peak"): 0.24,
    ("Winter", "Weekend", "Mid-Peak"): 0.6, ("Winter", "Weekend", "Super-Off-Peak"): 0.24,
    ("Summer", "Weekday", "Off-Peak"): 0.26, ("Summer", "Weekday", "On-Peak"): 0.63,
    ("Summer", "Weekend", "Mid-Peak"): 0.39, ("Summer", "Weekend", "Off-Peak"): 0.26
}

# SCE offers an EEC bonus for customers that enroll in the first year of the Solar Billing Program.  Set to 0 if this if not applicable.
BONUS = 0.04

# Surpress future warnings.
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define and write the header row to the output file
def write_header(outfile):
    header = ["Date", "StartTime", "EndTime", "kwHUsage", "Tag", "Season", "Year", "Month", "BillingSeason", "BillingDay", "TOU", "Cost"]
    df = pd.DataFrame(columns=header)
    df.to_csv(outfile, index=False)
    print("Header row written...")

# Parse the data from the input file and write it to the output file
def parse_data(infile, outfile):
    data_rows = []
    try:
        with open(infile, 'r', newline='') as f_in:
            reader = csv.reader(f_in)
            tag = ''
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
                        data_rows.append([date, startTime, endTime, kwHUsage, tag])
                elif "0NaN-NaN-NaN NaN:NaN:00Â\xa0 for NaN" in row[0]:
                     print("No data in the SCE_Usage.csv file.")
                     exit()
        df = pd.DataFrame(data_rows, columns=["Date", "StartTime", "EndTime", "kwHUsage", "Tag"])
        df.to_csv(outfile, mode='a', header=False, index=False)
        print("Primary data parsing complete...")
    except Exception as e:
        print(f"Error parsing data: {e}")

# Add the month and year to the output file
def enrich_data(outfile):
    try:
        data = pd.read_csv(outfile)
        data['Date'] = pd.to_datetime(data['Date'])
        data['Month'] = data['Date'].dt.strftime('%m').map(MONTH_MAP)
        data['Year'] = data['Date'].dt.year
        data['Season'] = data['Month'].map(SEASON_MAP)
        data['BillingSeason'] = data['Month'].map(BILLING_SEASON_MAP)
        data['BillingDay'] = data['Date'].dt.weekday.map(WEEKDAY_MAP)
        
        # Add TOU
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
        print("Data enrichment complete...")
    except Exception as e:
        print(f"Error enriching data: {e}")

#subtract the generated from delivered khw to get the net usage
def normalize_kwh(outfile):
    try:
        data = pd.read_csv(outfile)
        delivered = data[data['Tag'] == 'delivered']
        generated = data[data['Tag'] == 'generated']

        merged = pd.merge(delivered, generated, on=['Date', 'StartTime', 'EndTime'], suffixes=('_del', '_gen'))
        merged['net_kwHUsage'] = merged['kwHUsage_del'] - merged['kwHUsage_gen']
        data.update(merged[['Date', 'StartTime', 'EndTime', 'net_kwHUsage']])
        data.loc[data['Tag'] == 'delivered', 'kwHUsage'] = data['net_kwHUsage']
        data.drop(columns=['net_kwHUsage'], inplace=True)
        data.to_csv(outfile, index=False)
        print("Net usage calculated...")
    except Exception as e:
        print(f"Error calculating net usage: {e}")

# Add the delivery cost to the output file.
# The delivery cost is based on the billing season, billing day, and TOU.
# It is calculated as the product of the usage and the delivery cost.
# the del_costs dictionary is based on SCE's TOU-D-Prime rate schedule.
def add_delivery_cost(outfile):
    try:
        data = pd.read_csv(outfile)

        data['Cost'] = data.apply(
            lambda row: row['kwHUsage'] * DELIVERY_COSTS.get((row['BillingSeason'], row['BillingDay'], row['TOU']), 0) 
            if row['Tag'] == 'delivered' else 0, axis=1)
        data.to_csv(outfile, index=False)
        print("Delivery cost added...")
    except Exception as e:
        print(f"Error adding cost: {e}")

# Add the received value to the output file.
# The received value is based on the generated kwH. SCE's Pacific Time Zone ECC data found at: 
# https://www.sce.com/sites/default/files/custom-files/PDF_Files/EEC_Factors_Nov_2023.xlsx
def add_received_value(outfile):
    try:
        data = pd.read_csv(outfile)
        # Modify the path to match the location of your ECC_data.csv file
        ecc_data = pd.read_csv('/path/to/SCE/ECC_data.csv')
        data['StartTimeHour'] = pd.to_datetime(data['StartTime'], format='%H:%M:%S').dt.hour
        data['Month'] = pd.to_datetime(data['Date']).dt.month
        generated = data[data['Tag'] == 'generated']
        for idx, row in generated.iterrows():
            year, month, hour, is_weekend = row['Year'], row['Month'], row['StartTimeHour'], row['BillingDay'] == 'Weekend'
            ref_row = ecc_data[(ecc_data['Price Effective Date'] == year) & (ecc_data['Month'] == month) & (ecc_data['Hour'] == hour)]
            if not ref_row.empty:
                gen_cost = ref_row['SCE Gen - Weekend/Holiday EEC'].values[0] if is_weekend else ref_row['SCE Gen - Weekday EEC'].values[0]
                del_cost = ref_row['Delivery - Weekend/Holiday EEC'].values[0] if is_weekend else ref_row['Delivery - Weekday EEC'].values[0]
                bonus_value = row['kwHUsage'] * BONUS
                total_cost = row['kwHUsage'] * (gen_cost + del_cost + bonus_value)
                data.at[idx, 'Cost'] = total_cost
        data.to_csv(outfile, index=False)
        print("Generated value added...")
    except Exception as e:
        print(f"Error adding received value: {e}")

# Consolidate the SBP's 15 minute blocks of time into single hour blocks.
# This reduces the rows in the output file and make it easier to analyze in Excel as a Pivot Table.
def combine_data(outfile):
    try:
        data = pd.read_csv(outfile)
        data['Hour'] = pd.to_datetime(data['StartTime'], format='%H:%M:%S').dt.hour
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
        grouped_data.drop(columns=['Hour'], inplace=True)
        grouped_data.to_csv(outfile, index=False)
        print("Data combined...")
    except Exception as e:
        print(f"Error combining data: {e}")

# Main function to run the program
if __name__ == "__main__":
    # Modify the path to match the location of your SCE usage file
    input_file = "/path/to/sce_usage.csv"
    output_file = input_file.split('.')[0] + "_parsed.csv"

    write_header(output_file)
    parse_data(input_file, output_file)
    enrich_data(output_file)
    normalize_kwh(output_file)
    add_delivery_cost(output_file)
    add_received_value(output_file)
    combine_data(output_file)

    print("Parsing complete and stored in " + output_file)
