import requests
from bs4 import BeautifulSoup
import pickle
import sys
sys.setrecursionlimit(5000)
def scrape_actors(val):
    actors = []

    for i in range(val):
        if(i==0):
            URL = "https://films.lk/artists.php"
        else:
            URL = "https://films.lk/artists.php?page="+str(i+1)
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")

        results = soup.find_all(class_="row")
        actor_elements = results[1].find_all("div", class_="column2")
        for actor_element in actor_elements:
            title_element = actor_element.find("span", class_="eventTitle")
            period_element = actor_element.find("span", class_="period")
            link_element = actor_element.find_all("a")[0]
            actors.append([title_element, period_element, link_element['href']])
            print(title_element.text.strip())
            print(period_element.text.strip())
            print(link_element['href'])

    print(len(actors))
    with open('actors_names', 'wb') as fp:
        pickle.dump(actors, fp)


scrape_actors(10)