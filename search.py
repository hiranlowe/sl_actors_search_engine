from elasticsearch import Elasticsearch, helpers
import json
import re
from api.elastic_test import connect_elasticsearch
from scorpus.google_trans_new import google_translator

es = connect_elasticsearch()


def keyword_search(query):
    results = es.search(index='index-actors', body={
        "size": 500,
        "query": {
            "multi_match": {
                "query": query,
                "type": "best_fields",
                "fields": [
                    "name", "name_si",
                    "real_name", "real_name_si",
                    "birthday", "birthday_si",
                    "died", "died_si",
                    "address", "address_si",
                    "biography", "biography_si",
                    "awards.award_name",
                    "awards.award_fest",
                    "awards_si.award_name_si",
                    "awards_si.award_fest_si",
                    "filmography.film_title",
                    "filmography.role",
                    "filmography_si.film_title_si",
                    "filmography_si.role_si",
                    "image"],
                "fuzziness": 2,

            }

        },


        "aggs": {
            # "name": {
            #     "terms": {
            #         "field": "name_si.keyword",
            #         "size": 15
            #     }
            # },
            # "real_name": {
            #     "terms": {
            #         "field": "real_name_si.keyword",
            #         "size": 15
            #     }
            # },
            # "birthday": {
            #     "terms": {
            #         "field": "birthday_si.keyword",
            #         "size": 15
            #     }
            # },
            # "died": {
            #     "terms": {
            #         "field": "died_si.keyword",
            #         "size": 15
            #     }
            # },
            # "address": {
            #     "terms": {
            #         "field": "address_si.keyword",
            #         "size": 15
            #     }
            # },
            "awards": {
                "nested": {
                    "path": "awards_si"
                },
                "aggs": {
                    "awards_si.award_name_si": {
                        "terms": {
                            "field": "awards_si.award_name_si.keyword"
                        }
                    },
                    "awards_si.award_fest_si": {
                        "terms": {
                            "field": "awards_si.award_fest_si.keyword"
                        }
                    }
                }
            },
            "filmography": {
                "nested": {
                    "path": "filmography_si"
                },
                "aggs": {
                    "filmography_si.film_title_si": {
                        "terms": {
                            "field": "filmography_si.film_title_si.keyword"
                        }
                    },
                    "filmography_si.role_si": {
                        "terms": {
                            "field": "filmography_si.role_si.keyword"
                        }
                    }
                }
            },

        }

    })

    print(results)
    actors, awards_name, films_title, awards_fest, films_role = post_processing(
        results)
    return actors, awards_name, films_title, awards_fest, films_role


def filtered_search(query, award_name_filter, award_fest_filter, film_title_filter, film_role_filter):
    must_list = [{
        "multi_match": {
            "query": query,
            "type": "best_fields",
            "fields": [
                "name", "name_si",
                "real_name", "real_name_si",
                "birthday", "birthday_si",
                "died", "died_si",
                "address", "address_si",
                "biography", "biography_si",
                "awards.award_name",
                "awards.award_fest",
                "awards_si.award_name_si",
                "awards_si.award_fest_si",
                "filmography.film_title",
                "filmography.role",
                "filmography_si.film_title_si",
                "filmography_si.role_si",
                "image"],


        }
    }]
    if len(award_name_filter) != 0:
        for i in award_name_filter:
            must_list.append({
                "nested": {
                    "path": "awards_si",
                    "query": {
                        "match": {"awards_si.award_name_si": i}
                    }
                }
            })
    if len(award_fest_filter) != 0:
        for i in award_fest_filter:
            must_list.append({
                "nested": {
                    "path": "awards_si",
                    "query": {
                        "match": {"awards_si.award_fest_si": i}
                    }
                }
            })
    if len(film_title_filter) != 0:
        for i in film_title_filter:
            must_list.append({
                "nested": {
                    "path": "filmography_si",
                    "query": {
                        "match": {"filmography_si.film_title_si": i}
                    }
                }
            })
    if len(film_role_filter) != 0:
        for i in film_role_filter:
            must_list.append({
                "nested": {
                    "path": "filmography_si",
                    "query": {
                        "match": {"filmography_si.role_si": i}
                    }
                }
            })
    print(must_list)
    results = es.search(index='index-actors', body={
        "size": 500,
        "query": {
            "bool": {
                "must": must_list

            }
        },
        "aggs": {
            "awards": {
                "nested": {
                    "path": "awards_si"
                },
                "aggs": {
                    "awards_si.award_name_si": {
                        "terms": {
                            "field": "awards_si.award_name_si.keyword"
                        }
                    },
                    "awards_si.award_fest_si": {
                        "terms": {
                            "field": "awards_si.award_fest_si.keyword"
                        }
                    }
                }
            },
            "filmography": {
                "nested": {
                    "path": "filmography_si"
                },
                "aggs": {
                    "filmography_si.film_title_si": {
                        "terms": {
                            "field": "filmography_si.film_title_si.keyword"
                        }
                    },
                    "filmography_si.role_si": {
                        "terms": {
                            "field": "filmography_si.role_si.keyword"
                        }
                    }
                }
            },

        }
    })

    actors, awards_name, films_title, awards_fest, films_role = post_processing(results)
    return actors, awards_name, films_title, awards_fest, films_role


def get_best_query(search_query):
    translator = google_translator()
    search_query_en = translator.translate(search_query, lang_tgt='en')

    keywords_best_lower = ["top", "best", "popular", "good", "great", "actors", "acting", "acts", "great", "better"]
    keywords_best_upper = [x.upper() for x in keywords_best_lower]
    keywords_best_case = [x.title() for x in keywords_best_lower]
    keywords_best = keywords_best_case + keywords_best_upper + keywords_best_lower

    search_query_list = search_query_en.split()

    for item in search_query_list:
        try:
            y = int(item)
            is_int = True
            break
        except Exception as err:
            y = ''
            is_int = False
            print(err)
    if any(x in search_query_list for x in keywords_best):
        return True, is_int, y
    else:
        return False, is_int, y


def filtered_search_best(query, award_name_filter, award_fest_filter, film_title_filter, film_role_filter, val):
    must_list = []
    if len(award_name_filter) != 0:
        for i in award_name_filter:
            must_list.append({
                "nested": {
                    "path": "awards_si",
                    "query": {
                        "match": {"awards_si.award_name_si": i}
                    }
                }
            })
    if len(award_fest_filter) != 0:
        for i in award_fest_filter:
            must_list.append({
                "nested": {
                    "path": "awards_si",
                    "query": {
                        "match": {"awards_si.award_fest_si": i}
                    }
                }
            })
    if len(film_title_filter) != 0:
        for i in film_title_filter:
            must_list.append({
                "nested": {
                    "path": "filmography_si",
                    "query": {
                        "match": {"filmography_si.film_title_si": i}
                    }
                }
            })
    if len(film_role_filter) != 0:
        for i in film_role_filter:
            must_list.append({
                "nested": {
                    "path": "filmography_si",
                    "query": {
                        "match": {"filmography_si.role_si": i}
                    }
                }
            })
    print(must_list)
    results = es.search(index='index-actors', body={
        "query": {
            "bool": {
                "must": must_list

            }
        },
        "sort": [
            {
                "votes": {
                    "missing": "_last",
                    "order": "desc"
                }
            }
        ],
        "size": val or 500,
        "aggs": {
            "awards": {
                "nested": {
                    "path": "awards_si"
                },
                "aggs": {
                    "awards_si.award_name_si": {
                        "terms": {
                            "field": "awards_si.award_name_si.keyword"
                        }
                    },
                    "awards_si.award_fest_si": {
                        "terms": {
                            "field": "awards_si.award_fest_si.keyword"
                        }
                    }
                }
            },
            "filmography": {
                "nested": {
                    "path": "filmography_si"
                },
                "aggs": {
                    "filmography_si.film_title_si": {
                        "terms": {
                            "field": "filmography_si.film_title_si.keyword"
                        }
                    },
                    "filmography_si.role_si": {
                        "terms": {
                            "field": "filmography_si.role_si.keyword"
                        }
                    }
                }
            },

        }
    })

    actors, awards_name, films_title, awards_fest, films_role = post_processing(results)
    return actors, awards_name, films_title, awards_fest, films_role


def search_best(query, val):
    results = es.search(index='index-actors', body={
        "sort": [
            {
                "votes": {
                    "missing": "_last",
                    "order": "desc"
                }
            }
        ],
        "size": val or 500,
        "aggs": {
            "awards": {
                "nested": {
                    "path": "awards_si"
                },
                "aggs": {
                    "awards_si.award_name_si": {
                        "terms": {
                            "field": "awards_si.award_name_si.keyword"
                        }
                    },
                    "awards_si.award_fest_si": {
                        "terms": {
                            "field": "awards_si.award_fest_si.keyword"
                        }
                    }
                }
            },
            "filmography": {
                "nested": {
                    "path": "filmography_si"
                },
                "aggs": {
                    "filmography_si.film_title_si": {
                        "terms": {
                            "field": "filmography_si.film_title_si.keyword"
                        }
                    },
                    "filmography_si.role_si": {
                        "terms": {
                            "field": "filmography_si.role_si.keyword"
                        }
                    }
                }
            }

        }

    })

    actors, awards_name, films_title, awards_fest, films_role = post_processing(
        results)
    return actors, awards_name, films_title, awards_fest, films_role


def post_processing(results):
    actors = []
    for i in range(len(results['hits']['hits'])):
        actors.append(results['hits']['hits'][i]['_source'])
    aggregations = results['aggregations']
    # names = aggregations['name']['buckets']
    # real_names = aggregations['real_name']['buckets']
    # birthdays = aggregations['birthday']['buckets']
    # diedes = aggregations['died']['buckets']
    # addresses = aggregations['address']['buckets']
    awards_name = aggregations['awards']['awards_si.award_name_si']['buckets']
    films_title = aggregations['filmography']['filmography_si.film_title_si']['buckets']
    awards_fest = aggregations['awards']['awards_si.award_fest_si']['buckets']
    films_role = aggregations['filmography']['filmography_si.role_si']['buckets']
    return actors, awards_name, films_title, awards_fest, films_role


def search_filtered(query, award_name_filter, award_fest_filter, film_title_filter, film_role_filter):
    is_true, is_int, val = get_best_query(query)
    if is_true and is_int:
        actors, awards_name, films_title, awards_fest, films_role = filtered_search_best(query, award_name_filter,
                                                                                    award_fest_filter,
                                                                                    film_title_filter,
                                                                                    film_role_filter, val)
    elif is_true:
        actors, awards_name, films_title, awards_fest, films_role = filtered_search_best(query, award_name_filter,
                                                                                    award_fest_filter,
                                                                                    film_title_filter,
                                                                                    film_role_filter, None)
    else:
        actors, awards_name, films_title, awards_fest, films_role = filtered_search(query, award_name_filter,
                                                                                    award_fest_filter,
                                                                                    film_title_filter,
                                                                                    film_role_filter)
    return actors, awards_name, films_title, awards_fest, films_role


def search(query):
    is_true, is_int, val = get_best_query(query)
    print(is_true, val)
    if is_true and is_int:
        actors, awards_name, films_title, awards_fest, films_role = search_best(query, val)
    elif is_true:
        actors, awards_name, films_title, awards_fest, films_role = search_best(query, None)
    else:
        actors, awards_name, films_title, awards_fest, films_role = keyword_search(query)
    return actors, awards_name, films_title, awards_fest, films_role
