from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
        print("logged into account")

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
                experience_info["title"] = None

            try:
                experience_info["company_name_and_contract_type"] = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/div[1]/span[1]/span[1]").text
            except:
                experience_info["company_name_and_contract_type"] = None

            try:
                experience_info["dates"] = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/div[1]/span[2]/span[1]").text
            except:
                experience_info["dates"] = None

            try:
                experience_info["job_description"] = experience.find_element(By.XPATH, ".//div/div[2]/div[2]/ul/li[1]/div/ul/li/div/div/div/div/span[1]").text
            except:
                experience_info["job_description"] = None

            try:
                experience_info["skills"] = experience.find_element(By.XPATH, ".//div/div[2]/div[2]/ul/li[2]/div/ul/li/div/div/div/div/span[1]").text
            except:
                experience_info["skills"] = None

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
                education_info["school_name"] = None

            try:
                education_info["degree_type"] = education.find_element(By.XPATH, ".//div/div[2]/div/a/span[1]/span[1]").text
            except:
                education_info["degree_type"] = None

            try:
                education_info["school_years"] = education.find_element(By.XPATH, ".//div/div[2]/div/a/span[2]/span[1]").text
            except:
                education_info["school_years"] = None

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

class PDFGenerator:
    def generate_pdf(self, person, pdf_filename):
        print(f"generating pdf for {person.name}")
        # Create a PDF file
        c = canvas.Canvas(pdf_filename, pagesize=letter)

        # Add heading
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 725, "Curriculum Vitae")

        # Add sub-heading
        c.setFont("Helvetica-Bold", 12)
        c.drawString(120, 700, "Personal Information")
        c.setFont("Helvetica", 10)
        # Write the person's information to the PDF
        c.drawString(140, 680, person.name)
        c.drawString(140, 660, person.title)
        c.drawString(140, 640, person.location)

        # Experiences
        c.setFont("Helvetica-Bold", 12)
        c.drawString(120, 620, "Experiences:")
        c.setFont("Helvetica", 12)
        y = 600
        for experience in person.experiences:
            if experience["title"] is None and experience["company_name_and_contract_type"] is None and experience["dates"] is None and experience["job_description"] is None and experience["skills"] is None:
                pass
            else:
                if experience["title"] is not None:
                    c.setFillColorRGB(0, 0, 0, 1)
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(140, y, experience["title"])
                    y -= 20
                if experience["company_name_and_contract_type"] is not None:
                    c.setFillColorRGB(0, 0, 0, 1)
                    c.setFont("Helvetica", 10)
                    c.drawString(140, y, experience["company_name_and_contract_type"])
                    y -= 20
                if experience["dates"] is not None:
                    c.setFillColorRGB(0, 0, 0, 0.6)
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawString(140, y, experience["dates"])
                    y -= 20
                if experience["job_description"] is not None:
                    c.setFillColorRGB(0, 0, 0, 1)
                    c.setFont("Helvetica", 8)
                    job_description_lines = experience["job_description"].split('\n')
                    for line in job_description_lines:
                        c.drawString(140, y, line)
                        y -= 20
                if experience["skills"] is not None:
                    c.setFillColorRGB(0, 0, 0, 1)
                    c.setFont("Helvetica", 8)
                    c.drawString(140, y, experience["skills"])
                    y -= 20

        # Education
        c.setFillColorRGB(0, 0, 0, 1)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(120, y - 20, "Education:")
        c.setFont("Helvetica", 10)
        y -= 40
        for education in person.education:
            if education["school_name"] is None and education["degree_type"] is None and education["school_years"] is None:
                pass
            else:
                if education["school_name"] is not None:
                    c.setFillColorRGB(0, 0, 0, 1)
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(140, y, education["school_name"])
                    y -= 20
                if education["degree_type"] is not None:
                    c.setFillColorRGB(0, 0, 0, 1)
                    c.setFont("Helvetica", 8)
                    c.drawString(140, y, education["degree_type"])
                    y -= 20
                if education["school_years"] is not None:
                    c.setFillColorRGB(0, 0, 0, 0.6)
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawString(140, y, education["school_years"])
                    y -= 20


        # Save the PDF file
        c.save()
        print(f"PDF file '{pdf_filename}' created successfully.")
