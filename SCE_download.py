from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import getpass
import shutil
import os
from pathlib import Path

# Function to get the date range from the user
def get_date():
    today = datetime.date.today().strftime("%m/%d/%y")
    start_date = input(f"Enter the start date in the format MM/DD/YY: ")
    end_date = input(f"Enter the end date in format MM/DD/YY or press enter for {today}: ")

    if not end_date:
        return start_date, today
    
    return start_date, end_date

def user_pass():
    username = input("Enter your username: ")
    password = getpass.getpass(prompt="Enter your password: ")

    return username, password

def get_download_folder():
    if os.name == "nt":
        dl_folder = fr"{os.environ['USERPROFILE']}\Downloads"
    else:
        dl_folder = fr"{os.environ['HOME']}/Downloads"

    return dl_folder

def main():
    timeout = 10 #seconds

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the login page
        driver.get("https://www.sce.com/mysce/login")

        # Wait for the page to load
        wait = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//*[@id='userName']")))

        # Enter login credentials
        username, password = user_pass()
        username_input = driver.find_elements(By.XPATH, "//*[@id='userName']")
        password_input = driver.find_elements(By.XPATH, "//*[@id='password']")
        logon_button = driver.find_elements(By.XPATH, "//*[@id='react-login-main']/div/div/section/div[3]/form/div[2]/div[4]/button")

        username_input[1].send_keys(username)
        password_input[1].send_keys(password)
        logon_button[0].click()

    except Exception as e:
        print(f"Login error: {e}")

    try:
        # Wait for the page to load
        time.sleep(timeout)

        noob_window = driver.find_elements(By.XPATH, "//*[@id='DSSModal']/div/div/div[1]/button")
        current_usage_button = driver.find_elements(By.XPATH, "//*[@id='react-login-main']/div/div/section/div[3]/form/div[2]/div[4]/button")

        if len(noob_window) != 0:
            noob_window[0].click()
            driver.get("https://www.sce.com/sma/ESCAA/EscGreenButtonData")
        else:
            driver.get("https://www.sce.com/sma/ESCAA/EscGreenButtonData")

    except Exception as e:
        print(f"Navigation error: {e}")

    try:    
        # Wait for the page to load
        wait = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//*[@id='datadownload-content']/div/div/div/section/div/div[2]/div[4]/div[2]/div/div/div[2]")))  

        # Click on elements and enter date range
        download_data_button = driver.find_element(By.XPATH, "//*[@id='datadownload-content']/div/div/div/section/div/div[2]/div[4]/div[2]/div/div/div[2]")
        download_data_button.click()
        
        # Function to get the date range from the user
        dates = get_date() 

        from_date_range_input = driver.find_element(By.XPATH, "//*[@id='fromDateTextBox']")
        to_date_range_input = driver.find_element(By.XPATH, "//*[@id='toDateTextBox']")

        from_date_range_input.send_keys(dates[0])
        to_date_range_input.send_keys(dates[1])

        csv_radio_button = driver.find_element(By.XPATH, "//*[@id='datadownload-content']/div/div/div/section/div/div[2]/div[3]/div[2]/fieldset/ul/li[1]/div/label/input")
        csv_radio_button.click()

        # Click on reCaptcha checkbox
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
        input("Press Enter when done with Recaptcha and downloading the file...")
    except Exception as e:
        print(f"Date rangee, CSV radio button, or Recpatcha error: {e} ")

    # Close the webdriver
    driver.quit()

    try:
        # Rename the downloaded file
        new_start_date = dates[0].replace("/", "-")
        new_end_date = dates[1].replace("/", "-")

        # Move the downloaded file to the correct location
        
        dl_folder = get_download_folder()
        
        source = fr"{dl_folder}/SCE_Usage_YourAccountNumberHere_{new_start_date}_to_{new_end_date}.csv"
        dest = r"SCE_Usage.csv"
        shutil.move(source, dest)
        print("File moved successfully!")
    except Exception as e:
        print(f"File move error: {e}")

# Main function to run the program
if __name__ == "__main__":


    main()
    print("Done!")

