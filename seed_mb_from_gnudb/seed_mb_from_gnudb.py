#!/usr/bin/env python3
#
# Copyright (c) Jörg Mische <bobbl@gmx.de>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# 
# SPDX-License-Identifier: 0BSD


import random
import sys
import urllib.request

import discid # wrapper for libdiscid from MusicBrainz




option_choose_match = -2 # last match
option_delimiter    = " / "
option_multiple     = False
option_server       = "http://gnudb.gnudb.org:80" # protocol hostname port
option_username     = f"user{random.getrandbits(32):08x}+localhost"



def parse_args():
    global option_choose_match
    global option_delimiter
    global option_multiple
    global option_server
    global option_username

    for arg in sys.argv[1:]:
        if arg=="-h":
            print(f"Usage: {sys.argv[0]} [options]\n\n"
                "  -h       this help\n"
                "  -c<num>  number of the match to choose (1=first, default: last)\n"
                "  -d<str>  set delimiter between title and artist (default: -s' / ')\n"
                "  -m       prompt for multiple discs\n"
                "  -s<str>  set protocol, hostname and port of CDDB server (default: -shttp://gnudb.gnudb.org:80)\n"
                "  -u<str>  set username for gnudb (default: -uuserXXXXXXXX+localhost)\n"
                )
            exit(1)
        elif arg[:2]=='-c':
            option_choose_match = int(arg[2:])
        elif arg[:2]=='-d':
            option_delimiter = arg[2:]
        elif arg=='-m':
            option_multiple = True
        elif arg[:2]=='-s':
            option_server = arg[2:]
        elif arg[:2]=='-u':
            option_username = arg[2:]
        else:
            print(f"Unknown argument {arg}", file=sys.stderr)
            exit(2)



def print_response(r):
    print("----------------------------------")
    print(r, end="")
    print("----------------------------------")



def split_artist(artist_and_title, separator):
    pos = artist_and_title.find(separator)
    if pos >= 0:
        artist = artist_and_title[0:pos]
        title = artist_and_title[pos+len(separator):]
    else:
        artist = ""
        title = artist_and_title
    return artist, title



def gnudb_command(command):
    url = (f"{option_server}/~cddb/cddb.cgi?cmd={command}&" +
           f"hello={option_username}+seed_mb_from_gnudb+1.1&proto=6")

    with urllib.request.urlopen(url) as response:
        content = response.read().decode()
        assert response.status == 200
    return content



# query gnudb for a matching cd
# mbdisc : class discid.Disc
def gnudb_query_cd(mbdisc):
    ofsstr = "+".join([str(t.offset) for t in mbdisc.tracks])
    response = gnudb_command(
        f"cddb+query+{mbdisc.freedb_id}+{mbdisc.last_track_num}+" +
        ofsstr +
        f"+{mbdisc.seconds}")
    print("\nMatching entries in gnudb/FreeDB:")
    print_response(response)

    code = response[0:4]
    lines = response.splitlines()
    if code=="200 ":
        # "200 Found exact match"
        words = lines[1].split(" ")
    elif code=="210 ":
        # "210 Found exact matches, list follows (until terminating `.')"
        words = lines[option_choose_match].split(" ")
    else:
        print("Bad response to query for matches", file=sys.stderr)
        exit(3)

    return words[0], words[1]



# read one entry
def gnudb_read_entry(category, dischash):

    response = gnudb_command(f"cddb+read+{category}+{dischash}")
    if option_choose_match < 0:
        print("\nTracklist for last matching entry:")
    else:
        print(f"\nTracklist for entry {option_choose_match}:")
    print_response(response)

    if response[0:4]!="210 ":
        print("Bad response to read entry", file=sys.stderr)
        exit(4)

    tracks = []
    lines = response.splitlines()
    for line in lines:
        words = line.split("=", 1)
        if words[0]=="DTITLE":
            artist, title = split_artist(words[1], option_delimiter)
        elif words[0]=="DYEAR":
            year = words[1]
        elif words[0]=="DGENRE":
            genre = words[1]
        elif words[0][:6]=="TTITLE":
            try:
                track_no = int(words[0][6:])
                assert track_no == len(tracks)
            except:
                print("Invalid track number or not in order '{words[0]}'", file=sys.stderr)
                exit(5)
            a, t  = split_artist(words[1], option_delimiter)
            tracks.append({'artist': a, 'title': t})
        # ignore other keywords

    return {
        'title': title,
        'artist': artist,
        'year': year,
        'genre': genre,
        'tracks': tracks,
    }





def write_submit_file(all_discs):
    # HTML source: http://wiki.musicbrainz.org/Development/Release_Editor_Seeding -->

    fileName = "submit_" + ''.join(ch for ch in all_discs[0]['title'] if ch.isalnum()) + ".html"
    with open(fileName, 'w') as f:

        f.write("""\
<!DOCTYPE html>
<html>
  <head>
    <title>Seed to MusicBrainz</title>
    <style type="text/css">input[type=text] {{ width: 32em; margin: 1px; }}</style>
  </head>
  <body>
    <form  name="form" id="form" action="https://musicbrainz.org/release/add" method="post">
      <fieldset>
        <legend>Release information</legend>
        <label>Release name:</label>
        <input name="name" type="text" value="{title}" /><br>
        <label>Release artists as credited:</label>
        <input name="artist_credit.names.0.name" placeholder="name as credited" type="text" value="{artist}"/><br>
        <label>Release year:</label>
        <input name="events.0.date.year" placeholder="YYYY" type="text" value="{year}" /><br>
        <label>Release packaging:</label>
        <input name="packaging" type="text" value="jewel case" /><br>
      </fieldset>
""".format(title=all_discs[0]['title'],artist=all_discs[0]['artist'],year=all_discs[0]['year']))

        for x, one_disc in enumerate(all_discs):
            f.write(f'      <fieldset>\n'
                    f'        <label>Medium:</label>\n'
                    f'        <input name="mediums.{x}.format" '
                    f'placeholder="medium format" type="text" value="CD" /><br>\n'
                    f'        <legend>Tracklist of disc {x+1}</legend>')
            for y, track in enumerate(one_disc['tracks']):
                f.write(f'        <input name="mediums.{x}.track.{y}.artist_credit.names.0.name" '
                        f'type="text" value="{track["artist"]}" />\n'
                        f'        <input name="mediums.{x}.track.{y}.name" '
                        f'type="text" value="{track["title"]}" /><br>\n'
                )
            f.write(f'        <label>TOC string:</label>\n'
                    f'        <input style="width:60em" name="mediums.{x}.toc" '
                    f'placeholder="cd toc" type="text" value="{one_disc['toc_str']}" /><br>\n'
                    f'    </fieldset>\n')

        f.write('      <input type="submit" value="seed">\n'
                '    </form>\n'
                '  </body>\n'
                '</html>\n')

    print(f"Submit file written to '{fileName}'")




if __name__ == '__main__':

    parse_args()

    all_discs = []
    discno = 0
    while True:
        print(f"\nDisc {discno+1}\n========")

        d = discid.read()
        print(f"FreeDB: {d.freedb_id} MusicBrainz: {d.id}")
        print(f"MusicBrainz URL: {d.submission_url}")

        # query gnudb
        category, dischash = gnudb_query_cd(d)
        disc_info = gnudb_read_entry(category, dischash)
        disc_info['toc_str'] = d.toc_string

        print("\nProcessed result:")
        print(disc_info)
        all_discs.append(disc_info)

        if option_multiple == False:
            break

        answer = input("Press Enter to add another disc or anything else to stop: ")
        if (answer!=""):
            break

        discno += 1

    write_submit_file(all_discs)



