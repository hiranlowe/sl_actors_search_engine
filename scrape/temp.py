import requests
from bs4 import BeautifulSoup

URL = "https://films.lk/sinhala-cinema-artist-rukmani-devi-21.html"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find_all("ul")

name = results[0].find_all("li")[0].text.split(':')[-1].strip()
name_si = results[0].find_all("li")[1].text.split(':')[-1].strip()
real_name = results[0].find_all("li")[2].text.split(':')[-1].strip()
birthday = results[0].find_all("li")[3].text.split(':')[-1].strip()
died = results[0].find_all("li")[4].text.split(':')[-1].strip()

awards = soup.find_all("div", class_="row")[2].find_all("div", class_="column22")
awards_dict = {
    'award_name': '',
    'award_fest': ''
}
awards_list=[]
for award in awards[:11]:
    awards_dict['award_name'] = award.find("p").text[2:].split(" ")[0] + " " + awards[0].find("p").text[2:].split(" ")[1]
    awards_dict['award_fest'] = award.find("div").find("span").text
    awards_list.append(awards_dict)

films = soup.find_all("div", class_="row")[3].find_all("div", class_="column")[0].find("table").find_all("tr")
films_dict = {
    'film_title':'',
    'role':''
}
films_list=[]
for film in films[:11]:
    films_dict['film_title'] = film.find_all("td")[1].find("a").text
    films_dict['role'] = film.find_all("td")[1].find("span").text
    films_list.append(films_dict)

biography = soup.find_all("div", class_="row")[3].find_all("div", class_="column")[1].find_all("p")[0].text

temp = {
'name':name,
'name_si':name_si,
'real_name':real_name,
'birthday':birthday,
'died':died,
'awards': awards_list,
'filmography': films_list,
'biography':biography

}

print(temp)

