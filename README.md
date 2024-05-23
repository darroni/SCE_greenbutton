# SCE_greenbutton
This respository has code that automates most of the download process for Southern California Edison Solar Billing Plan, CSV-formated greenbutton usage data.  The code parses that greenbutton data into a more Excel friendly format and uses SCE's rate schedule for TOU-D-Prime to calculate estimated delivery costs and SCE's Energy Export Credit schedule to calculate generated costs.

Included are:
  - A Python script that downloads greenbutton data from SCE (SCE_download.py)
  - A Ptyhon script that parses the greenbutton data and calculates cost/value (SCE_parseGB.py)
  - Example SCE's Solar Billing Plan greenbutton data file
  - Example SCE Energy Export Credit file
  - Example output file in CSV format
  - Example Excel file with Pivot Tables defined for kwH Used/Generated and Cost/Value
    
# Details
SCE_download.py

This script uses SELENIUM and the CHROME webdriver to launch a browser instance and go to https://www.sce.com/mysce/login.  It requires some manual interaction in the Python terminal:
  - SCE username
  - SCE password
  - Start download date in MM-DD-YY format
  - End download date in MM-DD-YY formate, or Enter for today

It also requires some manual interaction with the Chrome Browser:
  - Solve the ReCaptcha puzzle
  - Click the download button

One line of code requires an edit.
    
![image](https://github.com/darroni/SCE_greenbutton/assets/17322676/3c664962-76f2-40f7-b5d8-adbd92305cf0)
