import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

capabilities = DesiredCapabilities.CHROME.copy()
capabilities['acceptInsecureCerts'] = True
options = webdriver.ChromeOptions()

# NOTE : kept false because the page isnt responding to headless=true option.
options.headless = False
driver = webdriver.Chrome(desired_capabilities=capabilities, options=options)
current_dir = "/Users/akashkandarkar/Desktop/Mini_Scripting_project_2//csv_data/"
def check_exists_by_xpath(xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except Exception:
        return False
    return True


all_win_df = pd.DataFrame(columns=["wining_team","wining_year"])


try:
    driver.get("https://www.iplt20.com/teams")
    time.sleep(5)
    teams_list = driver.find_elements(By.XPATH, "//a[@class='w-100']")
    urls = []
    team_name = []
    for team in teams_list:
        urls.append(team.get_attribute('href'))
    for url in urls:
        driver.get(url)
        time.sleep(3)
        team_name = driver.title.split("|")[1]
        if check_exists_by_xpath("//div[@class='vn-trophyBtn']//span"):
            wins = driver.find_element(By.XPATH,"//div[@class='vn-trophyBtn']//span")
            total_wins = wins.text.split(",")
        else:
            total_wins = []
        if len(total_wins) > 0:
            for year in total_wins:
                data = {
                    'winning_team': team_name,
                    'winning_year': year
                }
                temp_df = pd.DataFrame(data, index=[0])
                row = {'winning_team': team_name, 'winning_year': year}
                all_win_df = pd.concat([all_win_df, pd.DataFrame.from_records([row])])
                # all_win_df = all_win_df.append(row, ignore_index=True)
    driver.quit()
    all_win_df.to_csv(current_dir + 'team_wins.csv', index=False)

except Exception as e:
    print(e.with_traceback())
    driver.quit()