import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

current_dir = os.getcwd()
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['acceptInsecureCerts'] = True
options = webdriver.ChromeOptions()

# NOTE : kept false because the page isnt responding to headless=true option.
options.headless = False
driver = webdriver.Chrome(desired_capabilities=capabilities, options=options)

year_from = 2008
year_to = 2024
data_folder = "/Users/akashkandarkar/Desktop/Mini_Scripting_project_2/data/"


def check_exists_by_xpath(xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except Exception:
        return False
    return True


try:
    for year in range(year_from, year_to):
        print("Year:", year)
        driver.get("https://www.iplt20.com/stats/" + str(year))
        time.sleep(15)
        view_all = driver.find_elements(By.XPATH, "//div[@class='np-mostrunsTab__btn view-all']//a[text()='View All']")
        y_relative_coord = view_all[0].location['y']
        browser_navigation_panel_height = driver.execute_script('return window.outerHeight - window.innerHeight;')
        y_absolute_coord = y_relative_coord + browser_navigation_panel_height
        x_absolute_coord = view_all[0].location['x']
        driver.execute_script("window.scrollTo(0," + str(y_relative_coord - 110) + ")")
        time.sleep(1)
        load_more_new = driver.find_elements(By.XPATH,
                                             "//div[@class='np-mostrunsTab__btn view-all']//a[text()='View All']")
        load_more_new[0].click()
        print("All data loaded")
        if check_exists_by_xpath("//table[@class='st-table statsTable ng-scope archiveseason']"):
            table = driver.find_element(By.XPATH, "//table[@class='st-table statsTable ng-scope archiveseason']")
        elif check_exists_by_xpath("//table[@class='st-table statsTable ng-scope']"):
            table = driver.find_element(By.XPATH, "//table[@class='st-table statsTable ng-scope']")
        else:
            print("Table not found for ", year)
            break
        page_source = table.get_attribute('outerHTML')
        print("Got page source")
        result = re.sub(r"^.*<tbody>", "<tbody>", page_source)
        table = "<html><body><table>" + result + "</body></html>"
        soup = BeautifulSoup(table, 'html.parser')
        table = soup.find('table')
        var_name = f"batting_df_{year}"
        df = pd.read_html(str(table))[0]
        df = df.assign(season_year=year)
        df['team'] = df['Player'].str.extract(r'([A-Z]+)$')
        df['Player'] = df['Player'].str.replace('|'.join(df['team']), '')
        df.to_csv(current_dir+'/csv_data/'+str(var_name) + '.csv', index=False)
        # with open(data_folder + str(year) + "_batting_data.html", 'w') as f:
        #     pass
        # filename = data_folder + str(year) + "_batting_data.html"
        # file = open(filename, "w")
        # file.write(table)
    driver.quit()

except Exception as e:
    print(e.with_traceback())
    # driver.quit()
