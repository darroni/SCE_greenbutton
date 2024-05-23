# SCE_greenbutton
This respository has code that automates most of the download process for Southern California Edison Solar Billing Plan, CSV-formated greenbutton usage data.  The code parses that greenbutton data into a more Excel friendly format and uses SCE's rate schedule for TOU-D-Prime to calculate estimated delivery costs and SCE's Energy Export Credit schedule to calculate generated costs.

Included are:
  - A Python script that downloads greenbutton data from SCE (SCE_download.py)
  - A Ptyhon script that parses the greenbutton data and calculates cost/value (SCE_parse.py)
  - Example SCE's Solar Billing Plan greenbutton data file
  - Example SCE Energy Export Credit file
  - Example output file in CSV format
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
