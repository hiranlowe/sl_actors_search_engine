from elasticsearch.helpers import streaming_bulk

from api.elastic_test import connect_elasticsearch
from elasticsearch import helpers
import json
import pickle
from google_trans_new import google_translator
from datetime import datetime
import codecs
import tqdm

es = connect_elasticsearch()


def create_index():
    with open('actors', 'rb') as fp:
        actors = pickle.load(fp)
    actors_data = []
    translator = google_translator()
    for idx, actor in enumerate(actors[181:201]):
        real_name_si = translator.translate(actor[0].get('real_name'), lang_tgt='si')
        birthday_si = translator.translate(actor[0].get('birthday'), lang_tgt='si')
        died_si = translator.translate(actor[0].get('died'), lang_tgt='si')
        address_si = translator.translate(actor[0].get('address'), lang_tgt='si')
        try:
            biography_si = translator.translate(actor[0].get('biography'), lang_tgt='si')
        except Exception as er:
            biography_si = ''
        filmography_si = []
        awards_si = []
        # print(actor)
        for film in actor[0].get('filmography'):
            # print(film)
            filmoro = {
                'film_title_si': translator.translate(film.get('film_title'), lang_tgt='si'),
                'role_si': translator.translate(film.get('role'), lang_tgt='si'),
            }
            filmography_si.append(filmoro)

        for award in actor[0].get('awards'):
            awar = {
                'award_name_si': translator.translate(award.get('award_name'), lang_tgt='si'),
                'award_fest_si': translator.translate(award.get('award_fest'), lang_tgt='si'),
            }
            awards_si.append(awar)

        data = {
            'name': actor[0].get('name'),
            'name_si': actor[0].get('name_si'),
            'real_name': actor[0].get('real_name'),
            'real_name_si': real_name_si,
            'birthday': actor[0].get('birthday'),
            'birthday_si': birthday_si,
            'died': actor[0].get('died'),
            'died_si': died_si,
            'address': actor[0].get('address'),
            'address_si': address_si,
            'awards': actor[0].get('awards'),
            'awards_si': awards_si,
            'filmography': actor[0].get('filmography'),
            'filmography_si': filmography_si,
            'biography': actor[0].get('biography'),
            'biography_si': biography_si,
            'votes': actor[0].get('votes'),
            'rating': actor[0].get('rating'),
            'image': actor[0].get('image')

        }

        actors_data.append(data)
        print(data)
    with open('actors.json', encoding='utf8') as f:
        json_data = json.load(f)

    json_data = json_data + actors_data

    with open('actors.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False)


def start_index():
    with open('actors.json', encoding='utf8') as f:
        data = json.loads(f.read())
    print(data)
    with open('stopwords.txt', encoding='utf8') as file:
        lines = file.readlines()
        stopwords = [line.rstrip() for line in lines]
    print(stopwords)
    # helpers.bulk(es, data, index='index-actors')
    es.indices.create(
        index="index-actors",
        body={
            "settings": {
                "number_of_shards": 1,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "tokenizer": "whitespace",
                            "filter": ["my_custom_stop_words_filter"]
                        }
                    },
                    "filter": {
                        "my_custom_stop_words_filter": {
                            "type": "stop",
                            "ignore_case": True,
                            "stopwords": stopwords
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "name_si": {"type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword"
                                    }
                                },
                                },
                    "real_name": {"type": "text"},
                    "real_name_si": {"type": "text",
                                     "fields": {
                                         "keyword": {
                                             "type": "keyword"
                                         }
                                     },
                                     },
                    "birthday": {"type": "text"},
                    "birthday_si": {"type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword"
                                        }
                                    },
                                    },
                    "died": {"type": "text"},
                    "died_si": {"type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword"
                                    }
                                },
                                },
                    "address": {"type": "text"},
                    "address_si": {"type": "text",
                                   "fields": {
                                       "keyword": {
                                           "type": "keyword"
                                       }
                                   },
                                   },
                    'awards': {"type": "nested",
                               "properties": {
                                   "award_name": {
                                       "type": "text"
                                   },
                                   "award_fest": {
                                       "type": "text"
                                   },
                               },
                               },
                    'awards_si': {"type": "nested",
                                  "properties": {
                                      "award_name_si": {
                                          "type": "text",
                                          "fields": {
                                              "keyword": {
                                                  "type": "keyword"
                                              }
                                          },
                                      },
                                      "award_fest_si": {
                                          "type": "text",
                                          "fields": {
                                              "keyword": {
                                                  "type": "keyword"
                                              }
                                          },
                                      },
                                  }, },
                    'filmography': {"type": "nested",
                                    "properties": {
                                        "film_title": {
                                            "type": "text"
                                        },
                                        "role": {
                                            "type": "text"
                                        },
                                    },
                                    },
                    'filmography_si': {"type": "nested",
                                       "properties": {
                                           "film_title_si": {
                                               "type": "text",
                                               "fields": {
                                                   "keyword": {
                                                       "type": "keyword"
                                                   }
                                               },
                                           },
                                           "role_si": {
                                               "type": "text",
                                               "fields": {
                                                   "keyword": {
                                                       "type": "keyword"
                                                   }
                                               },
                                           },
                                       },
                                       },
                    'biography': {"type": "text"},
                    'biography_si': {"type": "text"},
                    'votes': {"type": "double"},
                    'rating': {"type": "double"},
                    'image': {"type": "text"}
                }
            },
        },
        ignore=400,
    )
    progress = tqdm.tqdm(unit="docs", total=200)
    successes = 0
    for ok, action in streaming_bulk(
            client=es, index="index-actors", actions=data,
    ):
        progress.update(1)
        successes += ok
    print("Indexed %d/%d documents" % (successes, 200))


if __name__ == "__main__":
    # create_index()
    start_index()
