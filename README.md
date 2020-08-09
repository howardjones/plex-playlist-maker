# playlist-maker

Python 3.6 script to read the IMDB Top 250 from the Radarr API, and
create a playlist for all the movies in it (that you have) in your Plex Media Server.

    git clone https://github.com/howardjones/plex-playlist-maker.git
    cd plex-playlist-maker
    # create a config.ini (sample supplied)
    pip install -r requirements.txt
    python3 playlist-maker.py
    
# Notes

* Works for me! (August 2020)
* If something ever drops from the first spot of the Top 250 all the way out in one hit, it'll probably freak out.
* If two movies with the exact same name are released in the same year, and make it into the Top 250, that'll probably not work.
* There's a translation table in the script for cases where Radarr and IMDB (or Radarr and Plex) disagree about the exact spelling of a title.