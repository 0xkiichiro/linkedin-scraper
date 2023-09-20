from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from unidecode import unidecode
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
        contact_line = self.driver.find_elements(By.CLASS_NAME, "pv-text-details__left-panel")[1]
        person.location = contact_line.find_element(By.TAG_NAME, "span").text
        try:
            contacts_link = contact_line.find_elements(By.TAG_NAME, "span")[1]
            contacts_link.click()
            time.sleep(self.WAIT_TIME)
            modal = self.driver.find_element(By.CLASS_NAME, "artdeco-modal")
            contact_lines = modal.find_elements(By.TAG_NAME, "a")
            person.contacts["linkedin"] = contact_lines[0].text
            for line in contact_lines:
                text = line.text.strip()
                # Check if the line contains a LinkedIn profile link
                if "linkedin.com/in/" in text:
                    person.contacts["linkedin"] = text
                # Check if the line contains an email address
                elif "@" in text:
                    person.contacts["email"] = text
                print(line.text)
            modal.find_element(By.TAG_NAME, "button").click()
            time.sleep(self.WAIT_TIME)
        except:
            print(f"No contact information for {person.name}")
        
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
        print("Contacts:", person.contacts)
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
        self.contacts = {
            "linkedin": "",
            "email": "",
            "phone_number": "",
            "website": ""
        }

class PDFGenerator:
    def generate_pdf(self, person, pdf_filename):
        # Create a buffer for the PDF
        buffer = BytesIO()

        # Create a SimpleDocTemplate with the buffer
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Define styles
        styles = getSampleStyleSheet()
        # justified
        justified_style = ParagraphStyle(name='JustifiedStyle')
        justified_style.fontName = 'Helvetica'  # Use Calibri font
        justified_style.fontSize = 8  # Font size
        justified_style.alignment = 4  # Justified alignment (4=justify)
        # oblique
        oblique_style = ParagraphStyle(name='ItalicStyle')
        oblique_style.fontName = 'Helvetica'
        oblique_style.fontSize = 8
        oblique_style.textColor = (0, 0, 0, 0.6)  # (R, G, B, Opacity)
        oblique_style.alignment = 0  # Left alignment (adjust as needed)
        oblique_style.fontName = 'Helvetica-Oblique'  # Use an oblique font
        # subheading
        subheading_style = ParagraphStyle(name='SubheadingStyle')
        subheading_style.fontName = 'Helvetica-Bold'  # Font name
        subheading_style.fontSize = 9  # Font size
        subheading_style.alignment = 0  # Left alignment (adjust as needed)
        # regular8
        regular_style_8 = ParagraphStyle(name='RegularStyle8')
        regular_style_8.fontName = 'Helvetica'  # Font name
        regular_style_8.fontSize = 8  # Font size
        regular_style_8.alignment = 0  # Left alignment (adjust as needed)

        # Create Story (a list of elements that go into the PDF)
        story = []

        # Add heading
        heading = Paragraph("<b>Curriculum Vitae</b>", styles['Heading2'])
        story.append(heading)

        # Add sub-heading
        personal_info_heading = Paragraph("<b>Personal Information</b>", styles['Heading3'])
        story.append(personal_info_heading)

        # Add Personal Information
        personal_info_text = f"<b>Name:</b> {unidecode(person.name)}<br/><b>Title:</b> {unidecode(person.title)}<br/><b>Location:</b> {unidecode(person.location)}<br/>"
        personal_info = Paragraph(personal_info_text, regular_style_8)
        story.append(personal_info)

        # Add Experiences
        experiences_heading = Paragraph("<b>Experiences:</b>", styles['Heading3'])
        story.append(experiences_heading)

        for experience in person.experiences:
            if experience["title"] and experience["company_name_and_contract_type"]:
                if experience["title"] is not None:
                    exp_title = unidecode(experience["title"])
                    exp_title_paragraph = Paragraph(exp_title, subheading_style)
                    story.append(exp_title_paragraph)
                if experience["company_name_and_contract_type"] is not None:
                    exp_company = unidecode(experience["company_name_and_contract_type"]).replace("*", "·")
                    exp_company_paragraph = Paragraph(exp_company, regular_style_8)
                    story.append(exp_company_paragraph)
                if experience["dates"] is not None:
                    exp_dates = unidecode(experience["dates"]).replace("*", "·")
                    exp_dates_paragraph = Paragraph(exp_dates, oblique_style)
                    story.append(exp_dates_paragraph)
                if experience["job_description"] is not None:
                    exp_description = unidecode(experience["job_description"])
                    exp_description_paragraph = Paragraph(exp_description, justified_style)
                    story.append(exp_description_paragraph)
                if experience["skills"] is not None:
                    exp_skills = experience["skills"].replace("*", "·")
                    exp_skills_paragraph = Paragraph(exp_skills, regular_style_8)
                    story.append(exp_skills_paragraph)
                story.append(Spacer(1, 12))  # Add spacing between experiences

        # Add Education
        education_heading = Paragraph("<b>Education:</b>", styles['Heading3'])
        story.append(education_heading)

        for education in person.education:
            if education["school_name"]:
                if education["school_name"] is not None:
                    edu_school_name = unidecode(education["school_name"])
                    edu_school_name_paragraph = Paragraph(edu_school_name, subheading_style)
                    story.append(edu_school_name_paragraph)
                if education["degree_type"] is not None:
                    edu_degree_type = unidecode(education["degree_type"])
                    edu_degree_type_paragraph = Paragraph(edu_degree_type, regular_style_8)
                    story.append(edu_degree_type_paragraph)
                if education["school_years"] is not None:
                    edu_school_years = unidecode(education["school_years"])
                    edu_school_years_paragraph = Paragraph(edu_school_years, oblique_style)
                    story.append(edu_school_years_paragraph)
                story.append(Spacer(1, 12))  # Add spacing between education entries

        # Build the PDF
        doc.build(story)

        # Move the buffer position to the beginning
        buffer.seek(0)

        # Write the PDF to a file
        with open(pdf_filename, 'wb') as f:
            f.write(buffer.read())

        print(f"PDF file '{pdf_filename}' created successfully.")