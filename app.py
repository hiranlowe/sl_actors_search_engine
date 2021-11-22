from flask import Flask
from api.elastic_test import connect_elasticsearch
import pickle
from flask import jsonify, request
import requests
from flask import flash, render_template, request, redirect, jsonify
from search import search, search_filtered
import json
from flask_paginate import Pagination, get_page_args

es = connect_elasticsearch()


app = Flask(__name__)

# with open('scrape/actors_meta', 'rb') as fp:
#     actors = pickle.load(fp)
# r = requests.delete('http://localhost:9200/_all')
# print(r.json())
# print(actors[0])
# i=1
# for actor in actors:
#     actor_id = i
#     actor_obj = {
#         'id': actor_id,
#         'name': actor[0].get('name'),
#         'name_si': actor[0].get('name_si'),
#         'real_name': actor[0].get('real_name'),
#         'birthday': actor[0].get('birthday'),
#         'died': actor[0].get('died'),
#         'address': actor[0].get('address'),
#     }
#
#     result = es.index(index='actor', id=actor_id, document=actor_obj, request_timeout=30)
#     print(result)
#     i+=1


@app.route('/', methods=['GET', 'POST'])
def search_actor():
    global g_query
    global g_actors
    global g_awards_name
    global g_films_title
    global g_awards_fest
    global g_films_role
    query, actors, awards_name, films_title, awards_fest, films_role = '', '', '', '', '', ''
    search1 = False
    if request.method == 'POST':
        if 'search_form' in request.form:
            if request.form['query']:
                query = request.form['query']
                search1 = True
                print(query)
            else:
                query = ''
            actors, awards_name, films_title, awards_fest, films_role = search(query)
            print('------------------------------')
            g_query = query
            g_actors = actors
            g_awards_name = awards_name
            g_films_title = films_title
            g_awards_fest = awards_fest
            g_films_role = films_role
            print('------------------------------------')
            print(len(actors))
            return render_template('index_new.html', actors=actors, awards_name=awards_name, films_title=films_title,
                                   awards_fest=awards_fest, films_role=films_role, query=query,pagination='')

        elif 'filter_form' in request.form:
            print("------------------------")
            award_name_filter = []
            award_fest_filter = []
            film_title_filter = []
            film_role_filter = []
            for i in g_awards_name:
                if request.form.get(i["key"]):
                    award_name_filter.append(i["key"])
            for i in g_awards_fest:
                if request.form.get(i["key"]):
                    award_fest_filter.append(i["key"])
            for i in g_films_title:
                if request.form.get(i["key"]):
                    film_title_filter.append(i["key"])
            for i in g_films_role:
                if request.form.get(i["key"]):
                    film_role_filter.append(i["key"])
            print(g_films_role)
            print(film_role_filter)
            query = g_query
            actors, awards_name, films_title, awards_fest, films_role = search_filtered(query, award_name_filter,award_fest_filter,
                                                                               film_title_filter, film_role_filter)
            g_query = query
            g_actors = actors
            g_awards_name = awards_name
            g_films_title = films_title
            g_awards_fest = awards_fest
            g_films_role = films_role


            return render_template('index_new.html', actors=actors, awards_name=awards_name, films_title=films_title,
                               awards_fest=awards_fest, films_role=films_role, query=query, pagination=None)

        elif 'details' in request.form:
            print(request.form.get('details'))

            actor_index = request.form.get('details')

            data = g_actors[int(actor_index)-1]
            return render_template('description_new.html', actor_details=data)

    else:
        return render_template('index_new.html', actors='', awards_name='', films_title='', awards_fest='', films_role='', pagination=None)




if __name__ == '__main__':
    app.run()
