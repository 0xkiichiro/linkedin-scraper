from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class LinkedinScaper:
    
    def __init__(self):
        self.WAIT_TIME = 2
        self.options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(options=self.options)
        self.driver.maximize_window()
        self.driver.get('http://www.linkedin.com/login')
    
    def login(self, email, password):
        time.sleep(self.WAIT_TIME)

        #enter dummy acc
        email_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="session_key"]')
        password_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="session_password"]')

        email_input.send_keys(email)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(self.WAIT_TIME)

class ScrapePerson:
    def __init__(self):
        pass
    