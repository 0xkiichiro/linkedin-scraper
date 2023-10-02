from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from unidecode import unidecode
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class LinkedinScaper:
    def __init__(self):
        self.WAIT_TIME = 5
        self.options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(options=self.options)
        self.driver.maximize_window()
        self.driver.get("http://www.linkedin.com/login")
    
    def set_self_wait_time(self, NEW_WAIT_TIME):
        self.WAIT_TIME = NEW_WAIT_TIME
    
    def login(self, email, password):
        time.sleep(self.WAIT_TIME)

        email_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="session_key"]')
        password_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="session_password"]')

        email_input.send_keys(email)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(10) # fix later, this is a hack to manually surpass captcha
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
        # Check for about section
        try:
            about_section = self.driver.find_element(By.ID, "about")
            about_text = about_section.find_element(By.XPATH, ".//following-sibling::*[position() = 2]/div/div/div/span").text
            person.about_text = about_text
        except:
            person.about_text = None
        # Check for contacts
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
            modal.find_element(By.TAG_NAME, "button").click()
            time.sleep(self.WAIT_TIME)
        except:
            pass
        # todo: broke experience scraping whilst working on API, fix        
        # Scrape experiences
        experience_container = self.driver.find_element(By.CLASS_NAME, "pvs-list")
        experiences = experience_container.find_elements(By.XPATH, "*")
        for experience in experiences:
            try:
                multi_position = experience.find_element(By.TAG_NAME, "ul")
                positions = multi_position.find_elements(By.XPATH, "*")
                company_name = experience.find_element(By.XPATH, ".//div/div[2]/div[1]/a/div/div/div/div/span[1]").text
                print(f"multi position spotted, {len(positions)} for {company_name}")
                for position in positions:
                    experience_info = {
                        "company_name_and_contract_type": None,
                        "title": None,
                        "employment_type": None,
                        "location": None,
                        "dates": None,
                        "skills": None,
                        "job_description": None
                    }
                    experience_info["company_name_and_contract_type"] = company_name
                    position_data = position.find_element(By.TAG_NAME, "a")
                    try:
                        experience_info["title"] = position_data.find_element(By.XPATH, ".//div/div/div/div/span[1]").text
                    except:
                        experience_info["title"] = None
                    try:
                        sub_data = position_data.find_elements(By.XPATH, "./span")
                        for data in sub_data:
                            data_text = data.find_element(By.XPATH, "./span").text
                            if DataParser.is_employment_type(data_text):
                                experience_info["employment_type"] = data_text
                            else:
                                experience_info["employment_type"] = None

                            # Check if data_text is a location
                            if DataParser.is_location(data_text):
                                experience_info["location"] = data_text
                            else:
                                experience_info["location"] = None

                            # Check if data_text is a date
                            if DataParser.is_date(data_text):
                                experience_info["dates"] = data_text
                            else:
                                experience_info["dates"] = None
                    except:
                        pass
                    try:
                        skills = position.find_elements(By.TAG_NAME, "strong")
                        for skill in skills:
                            skill_details = skill.find_element(By.XPATH, "..")
                            skill_text = skill_details.text
                            if DataParser.is_skills(skill_text):
                                experience_info["skills"] = skill_text
                            elif DataParser.is_skills(skill_text):
                                experience_info["skills"] = None
                    except:
                        pass
                    try:
                        multi_job_description = position.find_element(By.XPATH, ".//div/div[2]/div[2]/ul/li[1]/div/ul/li/div/div/div/div/span[1]").text
                        # Check if multi_job_description is the same as skills, and set job_description accordingly
                        if multi_job_description == experience_info["skills"]:
                            experience_info["job_description"] = None
                        else:
                            experience_info["job_description"] = multi_job_description
                    except:
                        experience_info["job_description"] = None
                    person.experiences.append(experience_info)
            except:
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
        try:
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
        except:
            pass
        
        # Scrape Certifications
        try:
            certificates_section = self.driver.find_element(By.ID, "licenses_and_certifications")
            certificate_list = certificates_section.find_elements(By.XPATH, ".//following-sibling::*[position() = 2]/ul/*")
            for item in certificate_list:
                try:
                    certificate_name = item.find_element(By.XPATH, ".//div/div[2]/div/div[1]/div/div/div/div/span[1]").text
                except:
                    certificate_name = ""
                try:
                    certificate_issuer = item.find_element(By.XPATH, ".//div/div[2]/div/div[1]/span[1]/span[1]").text
                except:
                    certificate_issuer = ""
                try:
                    certicate_issue_date = item.find_element(By.XPATH, ".//div/div[2]/div/div[1]/span[2]/span[1]").text
                except:
                    certicate_issue_date = ""

                certificate_obj = {
                    "name": certificate_name,
                    "issuer": certificate_issuer,
                    "issue_date": certicate_issue_date
                }
                person.certificates.append(certificate_obj)
        except:
            pass

        # Scrape Languages
        try:
            languages_section = self.driver.find_element(By.ID, "languages")
            language_list = languages_section.find_elements(By.XPATH, ".//following-sibling::*[position() = 2]/ul/*")
            for item in language_list:
                language_name = item.find_element(By.XPATH, ".//span").text
                try:
                    language_proficiency = item.find_element(By.XPATH, ".//div/div[2]/div/div[1]/span/span[1]").text
                except:
                    language_proficiency = ""
                lang_obj = {
                 "name": language_name,
                 "proficiency": language_proficiency
                }
                person.languages.append(lang_obj)        
        except:
            pass

        print("Scraped Person Object:", person.name)
        return person.to_dict()

    def close_browser(self):
        self.driver.quit()

class Person:
    def __init__(self):
        self.name = ""
        self.title = ""
        self.location = ""
        self.about_text = ""
        self.experiences = []
        self.education = []
        self.certificates = []
        self.languages = []
        self.contacts = {
            "linkedin": "",
            "email": "",
            "phone_number": "",
            "website": ""
        }

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "location": self.location,
            "about_text": self.about_text,
            "experiences": self.experiences,
            "education": self.education,
            "certificates": self.certificates,
            "languages": self.languages,
            "contacts": self.contacts
        }

class DataParser:
    @staticmethod
    def is_employment_type(input_string):
        employment_types = ["Full-time", "Part-time", "Contract", "Temporary", "Freelance", "Internship", "Volunteer", "Self-employed", "Entrepreneur", "Apprenticeship"]
        # Check if the input string is in the employment_types array
        if input_string in employment_types:
            return True
        else:
            return False
        
    @staticmethod
    def is_location(input_string):
        location_types = ["On-site", "Hybrid", "Remote"]
        # Check if the input string is in the location_types array
        if input_string in location_types:
            return True
        else:
            return False
        
    @staticmethod
    def is_date(input_string):
        # Check if the string contains " - Present"
        if " - Present" in input_string:
            return True
        # Check if the string contains "·" and "mos" indicating a duration
        if "·" in input_string and "mos" in input_string:
            return True
        # Check if the string contains "·" and "yr" indicating a duration in years
        if "·" in input_string and "yr" in input_string:
            return True
        return False
    
    @staticmethod
    def is_skills(input_string):
    # Check if the string contains "skills"
        if "skills" in input_string.lower():
            return True
        return False

class PDFGenerator:
    def generate_pdf(self, person, pdf_filename):
        # Create a buffer for the PDF
        buffer = BytesIO()

        # Create a SimpleDocTemplate with the buffer
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Define styles
        styles = getSampleStyleSheet()
        # justified
        justified_style = ParagraphStyle(name="JustifiedStyle")
        justified_style.fontName = "Helvetica"  # Use Calibri font
        justified_style.fontSize = 8  # Font size
        justified_style.alignment = 4  # Justified alignment (4=justify)
        # oblique
        oblique_style = ParagraphStyle(name="ItalicStyle")
        oblique_style.fontName = "Helvetica"
        oblique_style.fontSize = 8
        oblique_style.textColor = (0, 0, 0, 0.6)  # (R, G, B, Opacity)
        oblique_style.alignment = 0  # Left alignment (adjust as needed)
        oblique_style.fontName = "Helvetica-Oblique"  # Use an oblique font
        # subheading
        subheading_style = ParagraphStyle(name="SubheadingStyle")
        subheading_style.fontName = "Helvetica-Bold"  # Font name
        subheading_style.fontSize = 9  # Font size
        subheading_style.alignment = 0  # Left alignment (adjust as needed)
        # regular8
        regular_style_8 = ParagraphStyle(name="RegularStyle8")
        regular_style_8.fontName = "Helvetica"  # Font name
        regular_style_8.fontSize = 8  # Font size
        regular_style_8.alignment = 0  # Left alignment (adjust as needed)

        # Create Story (a list of elements that go into the PDF)
        story = []

        # Add heading
        heading = Paragraph("<b>Curriculum Vitae</b>", styles["Heading2"])
        story.append(heading)

        # Add sub-heading
        personal_info_heading = Paragraph("<b>Personal Information</b>", styles["Heading3"])
        story.append(personal_info_heading)

        # Add Personal Information
        personal_info_text = f"<b>Name:</b> {unidecode(person['name'])}<br/><b>Title:</b> {unidecode(person['title'])}<br/><b>Location:</b> {unidecode(person['location'])}<br/>"
        personal_info = Paragraph(personal_info_text, regular_style_8)
        story.append(personal_info)

        if person["about_text"]:
            about_text = Paragraph(person["about_text"], regular_style_8)
            story.append(about_text)
            story.append(Spacer(1, 12))  # Add spacing between education entries

        # Add Experiences
        if len(person["experiences"]):
            experiences_heading = Paragraph("<b>Experiences:</b>", styles["Heading3"])
            story.append(experiences_heading)
            for experience in person["experiences"]:
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
        if len(person["education"]):
            education_heading = Paragraph("<b>Education:</b>", styles["Heading3"])
            story.append(education_heading)
            for education in person["education"]:
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

        # Add Certificates
        if len(person["certificates"]):
            certificates_heading = Paragraph("<b>Certificates:</b>", styles["Heading3"])
            story.append(certificates_heading)
            for certificate in person["certificates"]:
                certificate_name = unidecode(certificate["name"])
                certificate_name_paragraph = Paragraph(certificate_name, subheading_style)
                story.append(certificate_name_paragraph)
                certificate_issuer = unidecode(certificate["issuer"])
                certificate_issuer_paragraph = Paragraph(certificate_issuer, regular_style_8)
                story.append(certificate_issuer_paragraph)
                certificate_issue_date = unidecode(certificate["issue_date"])
                certificate_issue_date_paragraph = Paragraph(certificate_issue_date, oblique_style)
                story.append(certificate_issue_date_paragraph)
            story.append(Spacer(1, 12))  # Add spacing between education entries

        # Add Languages
        if len(person["languages"]):
            languages_heading = Paragraph("<b>Languages:</b>", styles["Heading3"])
            story.append(languages_heading)
            for language in person["languages"]:
                language_name = unidecode(language["name"])
                language_name_paragraph = Paragraph(language_name, regular_style_8)
                story.append(language_name_paragraph)
                if language["proficiency"] is not None:
                    language_proficiency = unidecode(language["proficiency"])
                    language_proficiency_paragraph = Paragraph(language_proficiency, oblique_style)
                    story.append(language_proficiency_paragraph)
                else:
                    language_proficiency = ""
                    language_proficiency_paragraph = Paragraph(language_proficiency, oblique_style)
                    story.append(language_proficiency_paragraph)
            story.append(Spacer(1, 12))  # Add spacing between education entries

        # Build the PDF
        doc.build(story)

        # Move the buffer position to the beginning
        buffer.seek(0)

        # Write the PDF to a file
        with open(pdf_filename, "wb") as f:
            f.write(buffer.read())

        print(f"PDF file {pdf_filename} created successfully.")