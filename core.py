from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class LinkedinScaper:
    
    def __init__(self):
        self.WAIT_TIME = 3
        self.options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(options=self.options)
        self.driver.maximize_window()
        self.driver.get('http://www.linkedin.com/login')
    
    def set_self_wait_time(self, NEW_WAIT_TIME):
        self.WAIT_TIME = NEW_WAIT_TIME
    
    def login(self, email, password):
        time.sleep(self.WAIT_TIME)

        email_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="session_key"]')
        password_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="session_password"]')

        email_input.send_keys(email)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(self.WAIT_TIME)
        print("logged in to account")
    
    def go_to_profile(self, profile_name):
        self.driver.get(f"http://www.linkedin.com/in/{profile_name}")
        time.sleep(self.WAIT_TIME)
        print(f"navigated to profile: {profile_name}")

    def scrape_person(self, profile_name):
        self.go_to_profile(profile_name)
        # todo: expand the experiences later. redirects to new page, have to update the capturing
        # try:
        #     show_all_experiences = self.driver.find_element(By.ID, "navigation-index-see-all-experiences")
        #     show_all_experiences.click()
        #     print("expanded all experiences")
        # except:
        #     print("all experiences already visible")

        # scrape generic info
        text_details = self.driver.find_element(By.CLASS_NAME, "pv-text-details__left-panel")
        name = text_details.find_elements(By.TAG_NAME, "div")[0].find_element(By.TAG_NAME, "h1").text
        title = text_details.find_elements(By.TAG_NAME, "div")[1].text
        location = self.driver.find_elements(By.CLASS_NAME, "pv-text-details__left-panel")[1].find_element(By.TAG_NAME, "span").text
        print(name)
        print(title)
        print(location)
        experience_container = self.driver.find_element(By.CLASS_NAME, "pvs-list")
        experiences = experience_container.find_elements(By.XPATH, "*")
        print(len(experiences))
        
        # scrape details for each experience
        for experience in experiences:
            title = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/div[1]/div/div/div/div/span[1]").text
            print(title)

            company_name_and_contract_type = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/div[1]/span[1]/span[1]").text
            print(company_name_and_contract_type)

            dates = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/div[1]/span[2]/span[1]").text
            print(dates)

            job_description = experience.find_element(By.XPATH, ".//div/div[2]/div[2]/ul/li[1]/div/ul/li/div/div/div/div/span[1]").text
            print(job_description)
            try:
                skills = experience.find_element(By.XPATH, ".//div/div[2]/div[2]/ul/li[2]/div/ul/li/div/div/div/div/span[1]").text
                print(skills)
            except:
                print(f"no skills for {company_name_and_contract_type}")

        # todo: scrape education
        self.close_browser()

    def close_browser(self):
        self.driver.quit()
    