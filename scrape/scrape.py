# import requests
#
# URL = "https://realpython.github.io/fake-jobs/"
# page = requests.get(URL)
#
# print(page.text)


import requests
from bs4 import BeautifulSoup
import pickle

with open('actors_names', 'rb') as fp:
    actors = pickle.load(fp)
print(actors)
actors_details = []

for i in actors:
    URL = "https://films.lk/" + str(i[-1])
    page = requests.get(URL)
    print(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find_all("ul")
    results_li = results[0].find_all("li")
    titles = []
    for result in results_li:
        titles.append(result.text.split(':')[0].strip())
    print(titles)
    if "Known As" in titles:
        name = results_li[titles.index("Known As")].text.split(':')[-1].strip()
    else:
        name = '-'

    if "Sinhala" in titles:
        name_si = results_li[titles.index("Sinhala")].text.split(':')[-1].strip()
    else:
        name_si = '-'

    if "Real Name" in titles:
        real_name = results_li[titles.index("Real Name")].text.split(':')[-1].strip()
    else:
        real_name = '-'

    if "Birthday" in titles:
        birthday = results_li[titles.index("Birthday")].text.split(':')[-1].strip()
    else:
        birthday = '-'

    if "Died" in titles:
        died = results_li[titles.index("Died")].text.split(':')[-1].strip()
    else:
        died = '-'

    if "Address" in titles:
        address = results_li[titles.index("Address")].text.split(':')[-1].strip()
    else:
        address = '-'

    rows = soup.find_all("div", class_="row")
    votes_text = rows[0].find("div", class_="sp_rating").find("div", class_="votes").text
    print(votes_text)
    for char in ['%', '', ' ', 'Vote(s)']:
        votes_text = votes_text.replace(char, "")
    votes = votes_text.strip().split("|")[1].strip()
    rating = votes_text.strip().split("|")[0].strip()
    print(votes)
    print(rating)

    try:
        image = rows[1].find_all("div")[0].find("img")['src']
        print(image)
        awards = rows[2].find_all("div", class_="column22")

        awards_list = []
        for award in awards[:11]:
            awards_dict = {
                'award_name': award.find("p").text[2:].split(" ")[0] + " " + awards[0].find("p").text[2:].split(" ")[1],
                'award_fest': award.find("div").find("span").text
            }
            awards_list.append(awards_dict)

        films = rows[3].find_all("div", class_="column")[0].find("table").find_all("tr")

        films_list = []

        for film in films[:11]:
            films_dict = {
                'film_title': film.find_all("td")[1].find("a").text,
                'role': film.find_all("td")[1].find("span").text
            }
            films_list.append(films_dict)
        print(films_list)
        if len(rows[3].find_all("div", class_="column")[1].find_all("p")) == 0:
            biography = rows[3].find_all("div", class_="column")[1].text
        else:
            biography = rows[3].find_all("div", class_="column")[1].find_all("p")[0].text
        temp = {
            'name': name,
            'name_si': name_si,
            'real_name': real_name,
            'birthday': birthday,
            'died': died,
            'address': address,
            'awards': awards_list,
            'filmography': films_list,
            'biography': biography,
            'votes': votes,
            'rating': rating,
            'image': image

        }
        actors_details.append([temp])
    except Exception as error:
        try:
            try:
                awards = rows[1].find("div", class_="column").find("table").find_all("tr")

                awards_list = []
                for award in awards[:11]:
                    awards_dict = {
                        'award_name': award.find_all("td")[1].find("span").text,
                        'award_fest': award.find_all("td")[2].find("a").find("div").text
                    }
                    awards_list.append(awards_dict)
            except Exception as err:
                awards = rows[1].find("div", class_="column").find("table").find_all("tr")

                awards_list = []
                for award in awards[:11]:
                    awards_dict = {
                        'award_name': award.find_all("td")[1].find("span").text,
                        'award_fest': award.find_all("td")[1].text.split(awards_dict['award_fest'])[0]
                    }

                    awards_list.append(awards_dict)

            films = rows[2].find_all("div", class_="column")[0].find("table").find_all("tr")

            films_list = []
            for film in films[:11]:
                films_dict = {
                    'film_title': film.find_all("td")[1].find("a").text,
                    'role': film.find_all("td")[1].find("span").text
                }
                films_list.append(films_dict)
            if len(rows[2].find_all("div", class_="column")[1].find_all("p")) == 1:
                biography = rows[2].find_all("div", class_="column")[1].find_all("p")[0].text
            else:
                biography = rows[2].find_all("div", class_="column")[1].text
            temp = {
                'name': name,
                'name_si': name_si,
                'real_name': real_name,
                'birthday': birthday,
                'died': died,
                'address': address,
                'awards': awards_list,
                'filmography': films_list,
                'biography': biography,
                'votes': votes,
                'rating': rating,
                'image': image

            }
            actors_details.append([temp])
            print(error)
        except Exception as er:
            temp = {
                'name': name,
                'name_si': name_si,
                'real_name': real_name,
                'birthday': birthday,
                'died': died,
                'address': address,
                'awards': [],
                'filmography': [],
                'biography': '-',
                'votes': votes,
                'rating': rating,
                'image': '-'

            }
            actors_details.append([temp])

with open('actors', 'wb') as fp:
    pickle.dump(actors_details, fp)

print(len(actors_details))
