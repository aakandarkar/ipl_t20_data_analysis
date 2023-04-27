import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import re
import pandas as pd
import os


current_dir = "/Users/akashkandarkar/Desktop/Mini_Scripting_project_2/"
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['acceptInsecureCerts'] = True
options = webdriver.ChromeOptions()
#NOTE : kept false because the page isnt responding to headless=true option.
options.headless = False
driver = webdriver.Chrome(desired_capabilities=capabilities,options=options)

year_from = 2008
year_to = 2024

def check_exists_by_xpath(xpath):
    try:
        driver.find_element(By.XPATH,xpath)
    except Exception:
        return False
    return True

cookie_block = True
try:
    for year in range(year_from, year_to):
        print("Year:",year)
        driver.get("https://www.iplt20.com/stats/"+str(year))
        time.sleep(15)

        if check_exists_by_xpath("//div[@class='cookie']//button[@class='cookie__accept cookie__accept_btn']") and cookie_block:
            print("Cookeie button")
            driver.find_element(By.XPATH,"//div[@class='cookie']//button[@class='cookie__accept cookie__accept_btn']").click()
            print("Cookeie button clicked")
            cookie_block = False
        drop_down = driver.find_element(By.XPATH,"//div[@class='col-lg-3 col-md-3 col-sm-12 statsFilter']//div[@class='cSBDisplay ng-binding']")
        drop_down.click()
        time.sleep(1)
        #bowler
        bowler_radio = driver.find_element(By.XPATH,"//div[@class='cSBListItemsFilter']//span[@class='cSBListFItems bowFItem']")
        bowler_radio.click()
        time.sleep(1)
        purple_cup = driver.find_element(By.XPATH,"//div[text()='Aramco Purple Cap']")
        purple_cup.click()
        time.sleep(10)
        print("Purple cap data loaded")
        view_all = driver.find_elements(By.XPATH,"//div[@class='np-mostrunsTab__btn view-all']//a[text()='View All']")
        print("View button found",view_all[1].location)
        y_relative_coord = view_all[1].location['y']
        print("y_relative_coord",y_relative_coord)
        browser_navigation_panel_height = driver.execute_script('return window.outerHeight - window.innerHeight;')
        print("browser_navigation_panel_height", browser_navigation_panel_height)
        y_absolute_coord = y_relative_coord + browser_navigation_panel_height
        print("y_absolute_coord", y_absolute_coord)
        x_absolute_coord = view_all[1].location['x']
        print("x_absolute_coord", x_absolute_coord)
        driver.execute_script("window.scrollTo(0,"+str(y_relative_coord-110)+")")
        print("Scrolled")
        time.sleep(1)
        load_more_new = driver.find_elements(By.XPATH, "//div[@class='np-mostrunsTab__btn view-all']//a[text()='View All']")
        print("loadmore : ", len(load_more_new))
        load_more_new[1].click()
        print("All data loaded")
        if check_exists_by_xpath("//table[@class='st-table statsTable ng-scope archiveseason']"):
            table = driver.find_element(By.XPATH,"//table[@class='st-table statsTable ng-scope archiveseason']")
        elif check_exists_by_xpath("//table[@class='st-table statsTable ng-scope']"):
            table = driver.find_element(By.XPATH, "//table[@class='st-table statsTable ng-scope']")
        else:
            print("Table not found for ",year)
            break
        page_source = table.get_attribute('outerHTML')
        print("Got page source")
        result = re.sub(r"^.*<tbody>", "<tbody>", page_source)
        table = "<html><body><table>"+result+"</body></html>"
        soup = BeautifulSoup(table, 'html.parser')
        table = soup.find('table')
        var_name = f"bowling_df_{year}"
        df = pd.read_html(str(table))[0]
        print(df)
        df = df.assign(season_year=year)
        df['team'] = df['Player'].str.extract(r'([A-Z]+)$')
        df['Player'] = df['Player'].str.replace('|'.join(df['team']), '')
        df.to_csv(current_dir + '/csv_data/' + str(var_name) + '.csv', index=False)
    driver.quit()

except Exception as e:
    print(e.with_traceback())
    #driver.quit()