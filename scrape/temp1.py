import requests
from bs4 import BeautifulSoup

URL = "https://films.lk/sinhala-cinema-artist-rukmani-devi-21.html"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")


films = soup.find_all("div", class_="row")[3].find_all("div", class_="column")[1].find_all("p")[0].text
print(films)