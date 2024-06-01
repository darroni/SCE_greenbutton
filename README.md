# SCE_greenbutton
This respository automates most of the download process for Southern California Edison Solar Billing Plan (SBP/NEMv3)'s greenbutton-formatted usage data.  It parses the greenbutton data into an 'Excel friendly' format and uses SCE's TOU-D-Prime and Energy Export Credits (ECC) rate schedules to calculate delivery cost and self-generated value.

This repo includes:
  - A Python script that downloads greenbutton data from SCE (SCE_download.py)
  - A Python script that parses the greenbutton data and calculates cost/value (SCE_parse.py)
  - A Python script that merges the data from the _parsed.csv file to the Excel file for analysis
  - An example SCE Solar Billing Plan greenbutton data file (Example_SCE_Usage.csv)
  - An example SCE Energy Export Credit file (ECC_data.csv)
  - Example output file in CSV format (Example_SCE_Usage_parsed.csv)
  - Example Excel file with Pivot Tables defined for kwH Used/Generated and Cost/Value
    
## Details
### SCE_download.py

This script uses SELENIUM and the CHROME webdriver to launch a browser instance and go to https://www.sce.com/mysce/login.  It requires some manual interaction in the Python terminal:
  - SCE username
  - SCE password
  - Start download date in MM-DD-YY format
  - End download date in MM-DD-YY formate, or Enter for today

It also requires some manual interaction with the Chrome Browser:
  - Solve the ReCaptcha puzzle
  - Click the download button

Add your SCE Account Number to the following line of code.
````
source = fr"{dl_folder}/SCE_Usage_YourAccountNumberHere_{new_start_date}_to_{new_end_date}.csv"
````

**NOTE:**  Make sure you match the version of the CHROMEDRIVER.EXE with your Chrome browser.

### SCE_parse.py

This script uses PANDAS, CSV, DATETIME, and WARNINGS to parse the SCE_Usage.csv file downloaded in SCE_download.py.  It massages the data to to meet my requirements and can certainly be improved upon or optimized.

The only variable tha might need to be changed is the location of your input file, or SCE_Usage.csv file.  Line 224 in the code can be modified to suit your needs.
````
input_file = "/path/to/your/sce_usage.csv"
````
### SCE_merged_data.py

This script uses PANDAS and OPENPYXL to copy and normalize the formating of the data in the _parsed.csv file to Excel.  It is copied in a data Table in Excel that is referenced by several pivot tables.

### SCE_runall.py

This script executes each script in sequence, minimizing manual interaction.

### When complete
With the SCE_usage_parsed.csv file populated, simply copy and past the data into the example Excel file for analysis or create your own data model.
