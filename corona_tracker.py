import requests
import json
import re

def corona_tracker(text):

    countries = []

    countries_url = "https://covid19.mathdro.id/api/countries"
    countries_response = requests.get(countries_url)
    countries_json_response = json.loads(countries_response.text)

    for country in countries_json_response['countries']:
        countries.append(country['name'].strip().lower())
    
    country = ""
    
    for i in countries:
        if re.search(i,text.lower()):
            country = i
            break

    if country:
        country_url = "https://covid19.mathdro.id/api/countries/"+country
        country_response = requests.get(country_url)
        country_json_response = json.loads(country_response.text)

        country_set = {}

        country_set["confirmed"] = country_json_response['confirmed']['value']
        country_set['recovered'] = country_json_response['recovered']['value']
        country_set['deaths'] = country_json_response['deaths']['value']

        return country_set

    else:
        
        main_url = "https://covid19.mathdro.id/api"
        main_response = requests.get(main_url)
        main_json_response = json.loads(main_response.text)

        global_set = {}

        global_set["confirmed"] = main_json_response['confirmed']['value']
        global_set['recovered'] = main_json_response['recovered']['value']
        global_set['deaths'] = main_json_response['deaths']['value']

        return global_set


