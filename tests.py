from core import LinkedinScaper
from core import PDFGenerator
import json

# init scraper
liscraper = LinkedinScaper()
# read userdata from json
with open("userdata.json", "r") as userdata:
    userdata = json.load(userdata)
# login
liscraper.login(userdata["email"], userdata["password"])

#starting to scrape
scrape_list = ["dorukylmz", "berk-özer-a30358b9", "alkan-kosar", "batu-buktel", "alper-batuhan-685272260", "barisaytimur", "cem-sarı-729b371b5", "cansu-özer-180003214", "başar-aytimur-266372250"]
for scrapee in scrape_list:
    person = liscraper.scrape_person(scrapee)
    pdf_generator = PDFGenerator()
    pdf_generator.generate_pdf(person, f"{scrapee}.pdf")


liscraper.close_browser()