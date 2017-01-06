"""Script that get entries from class learning journal site and adds to db."""

import requests


r = requests.get('http://sea-python-401d5.herokuapp.com/api/export?apikey=1214df86-0ddd-4def-a752-4366f681907c').json()

a = []

for entry in r:
    a.append({"title": entry["title"],
              "id": entry["id"],
              "creation_date": entry["created"],
              "body": entry["text"]})
