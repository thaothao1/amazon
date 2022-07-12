from distutils.command import check
from readline import clear_history
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
import sys

def zip_code(link):
    ua = UserAgent()
    ua.random
    print(ua.ie)

    user_amazon = "ntqp1997@gmail.com"
    pass_amazon = "123456"


    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    chrome_options.headless = True
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=" + ua.ie)
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url ='https://www.amazon.com/'


    driver.get(url)
    time.sleep(1)
    delivery_to = driver.find_element(By.XPATH,'//*[@id="glow-ingress-block"]')
    delivery_to.click()

    time.sleep(1)
    input_zip_code = driver.find_element(By.ID,'GLUXZipUpdateInput')
    input_zip_code.send_keys("90001")

    time.sleep(1)
    apply_button = driver.find_element(By.ID,'GLUXZipUpdate-announce')
    driver.execute_script("arguments[0].click();", apply_button)
 
    input_url =link
    # driver.get(input_url)
    

    # current_delivery = driver.find_element(By.XPATH,'//*[@id="glow-ingress-line2"]').get_attribute('innerHTML').strip()
    # print("Delivery To: " ,current_delivery)
    driver.quit()
    return input_url