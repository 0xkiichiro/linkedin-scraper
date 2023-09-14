from core import LinkedinScaper
import json

# init scraper
liscraper = LinkedinScaper()
# read userdata from json
with open("userdata.json", "r") as userdata:
    userdata = json.load(userdata)
# login
liscraper.login(userdata["email"], userdata["password"])
#starting to scrape
liscraper.scrape_person("alkan-kosar")
liscraper.scrape_person("batu-buktel")
liscraper.scrape_person("alper-batuhan-685272260")