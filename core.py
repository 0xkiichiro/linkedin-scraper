from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class LinkedinScaper:
    def __init__(self):
        self.WAIT_TIME = 5
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
        # time.sleep(15) # fix later, this is a hack to manually surpass captcha
        time.sleep(self.WAIT_TIME)
        print("logged in to account")

    def go_to_profile(self, profile_name):
        self.driver.get(f"http://www.linkedin.com/in/{profile_name}")
        time.sleep(self.WAIT_TIME)
        print(f"navigated to profile: {profile_name}")
    
    def scrape_person(self, profile_name):
        self.go_to_profile(profile_name)
        
        person = Person()
        
        # Scrape generic info
        text_details = self.driver.find_element(By.CLASS_NAME, "pv-text-details__left-panel")
        person.name = text_details.find_elements(By.TAG_NAME, "div")[0].find_element(By.TAG_NAME, "h1").text
        person.title = text_details.find_elements(By.TAG_NAME, "div")[1].text
        person.location = self.driver.find_elements(By.CLASS_NAME, "pv-text-details__left-panel")[1].find_element(By.TAG_NAME, "span").text
        
        # Scrape experiences
        experience_container = self.driver.find_element(By.CLASS_NAME, "pvs-list")
        experiences = experience_container.find_elements(By.XPATH, "*")
        
        for experience in experiences:
            experience_info = {}
            try:
                experience_info["title"] = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/div[1]/div/div/div/div/span[1]").text
            except:
                experience_info["title"] = "No title"

            try:
                experience_info["company_name_and_contract_type"] = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/div[1]/span[1]/span[1]").text
            except:
                experience_info["company_name_and_contract_type"] = "No company name | contract type"

            try:
                experience_info["dates"] = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/div[1]/span[2]/span[1]").text
            except:
                experience_info["dates"] = "No dates"

            try:
                experience_info["job_description"] = experience.find_element(By.XPATH, ".//div/div[2]/div[2]/ul/li[1]/div/ul/li/div/div/div/div/span[1]").text
            except:
                experience_info["job_description"] = f"No job desc for {experience_info['company_name_and_contract_type']}"

            try:
                experience_info["skills"] = experience.find_element(By.XPATH, ".//div/div[2]/div[2]/ul/li[2]/div/ul/li/div/div/div/div/span[1]").text
            except:
                experience_info["skills"] = f"No skills for {experience_info['company_name_and_contract_type']}"

            person.experiences.append(experience_info)
        
        # Scrape education
        education_header = self.driver.find_element(By.ID, "education")
        education_section = education_header.find_element(By.XPATH, "..")
        education_list = education_section.find_element(By.TAG_NAME, "ul")
        educations = education_list.find_elements(By.XPATH, "*")
        
        for education in educations:
            education_info = {}
            try:
                education_info["school_name"] = education.find_element(By.XPATH, ".//div/div[2]/div/a/div/div/div/div/span[1]").text
            except:
                education_info["school_name"] = "------"

            try:
                education_info["degree_type"] = education.find_element(By.XPATH, ".//div/div[2]/div/a/span[1]/span[1]").text
            except:
                education_info["degree_type"] = "------"

            try:
                education_info["school_years"] = education.find_element(By.XPATH, ".//div/div[2]/div/a/span[2]/span[1]").text
            except:
                education_info["school_years"] = "------"

            person.education.append(education_info)
        
        print("Scraped Person Object:")
        print("Name:", person.name)
        print("Title:", person.title)
        print("Location:", person.location)
        print("Experiences:", person.experiences)
        print("Education:", person.education)
        return person

    def close_browser(self):
        self.driver.quit()

class Person:
    def __init__(self):
        self.name = ""
        self.title = ""
        self.location = ""
        self.experiences = []
        self.education = []