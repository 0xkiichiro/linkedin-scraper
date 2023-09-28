from core import LinkedinScaper
from core import PDFGenerator
import json

# init scraper
liscraper = LinkedinScaper()
# read userdata from json
with open("userdata.json", "r") as userdata:
    userdata = json.load(userdata)
# login
liscraper.login(userdata[2]["email"], userdata[2]["password"])

#starting to scrape
scrape_list = ["dorukylmz", "berk-özer-a30358b9", "alkan-kosar", "batu-buktel", "alper-batuhan-685272260", "barisaytimur", "cem-sarı-729b371b5", "cansu-özer-180003214", "başar-aytimur-266372250"]
scrape_list_short = ["julian-r-gruber-a59652161", "agnemokrikaite", "batu-buktel", "barisaytimur", "başar-aytimur-266372250", "can-erdogan-", "batusozen"]
scrape_list_1 = ["can-erdogan-", "dora-dağlaraşar-30b004131", "zeynep-saygili-76962a34"]
scrape_list_2 = ["can-erdogan-"]
for scrapee in scrape_list_1:
    person = liscraper.scrape_person(scrapee)
    pdf_generator = PDFGenerator()
    pdf_generator.generate_pdf(person, f"{scrapee}.pdf")

liscraper.close_browser()