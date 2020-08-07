import json
import os
import requests
from configparser import ConfigParser
from plexapi.myplex import MyPlexAccount
from plexapi import playlist

""" Python 3.6 script to read the IMDB Top 250 from the Radarr API, and
create a playlist for all the movies in it (that you have) in your Plex Media Server.

"""

live = True

config = ConfigParser()
config.read("config.ini")

corrections = {
    "Ford v. Ferrari": "Ford v Ferrari"
}


def find_movie(library, wanted_title: str, wanted_year: int):
    if wanted_year == 0:
        wanted_year = 2020

    print(f"Searching for {wanted_title} ({wanted_year})")
    res = library.search(title=wanted_title, year=wanted_year, libtype='movie', maxresults=10)

    if len(res) == 1:
        print(f"  adding {res}")
        return res[0]

    if len(res) == 0:
        print("  No match.")
        return None

    if len(res) > 1:
        print("  Too many matches")
        print(res)
        added = False
        for r in res:
            if r.title == wanted_title:
                print(f"Adding {r} as exact match")
                added = True
                return r
        if not added:
            print("  No exact match.")
            return None

    return None


print("Loading Top 250 from JSON")
if os.path.isfile(config['DEFAULT']['cache_file']):
    print("f(cached local file - delete {config['DEFAULT']['cache_file']} to force a live reload")
    with open(config['DEFAULT']['cache_file'], "r") as f:
        top250 = json.load(f)
else:
    print("Loading live from source")
    res = requests.get(config['DEFAULT']['source_chart'])
    top250 = json.loads(res.text)
    with open(config['DEFAULT']['cache_file'], "w") as f:
        json.dump(top250, f)

print("Connecting to " + config['DEFAULT']['server'] + " (this takes a few seconds)")
account = MyPlexAccount(config['DEFAULT']['username'], config['DEFAULT']['password'])
plex = account.resource(config['DEFAULT']['server']).connect()  # returns a PlexServer instance

movies = plex.library.section('Movies')

my_playlist = None

first = top250.pop(0)
res = find_movie(movies, first['title'], int(first['release_year']))

if live:
    all_playlists = plex.playlists()
    print(all_playlists)

    for pl in all_playlists:
        if pl.title == config['DEFAULT']['playlist_name']:
            my_playlist = pl

    if my_playlist:
        existing = my_playlist.items()
        for i in my_playlist.items():
            if i != res:
                my_playlist.removeItem(i)
    else:
        print("Creating playlist")
        playlist.Playlist.create(plex, config['DEFAULT']['playlist_name'], [res])

    print("Finding playlist")
    my_playlist = plex.playlist(config['DEFAULT']['playlist_name'])

missed = []

for m in top250:
    title = m['title']
    if title in corrections:
        title = corrections[title]
    year = int(m['release_year'])

    print(f"Searching for {title} ({year})")
    res = find_movie(movies, title, year)
    if live:
        if res:
            my_playlist.addItems([res])
        else:
            missed.append(f"{title} ({year})")

print("DONE!")

for m in missed:
    print("MISSING: " + m)
