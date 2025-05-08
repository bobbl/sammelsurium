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


import json
import sys

import discid
import freedb



def write_submit_file(all_discs):
    # HTML source: http://wiki.musicbrainz.org/Development/Release_Editor_Seeding -->

    fileName = "submit_" + ''.join(ch for ch in all_discs[0]['release'] if ch.isalnum()) + ".html"
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
        <input name="name" type="text" value="{release}" /><br>
        <label>Release artists as credited:</label>
        <input name="artist_credit.names.0.name" placeholder="name as credited" type="text" value="{artist}"/><br>
        <label>Release year:</label>
        <input name="events.0.date.year" placeholder="YYYY" type="text" value="{year}" /><br>
        <label>Release packaging:</label>
        <input name="packaging" type="text" value="jewel case" /><br>
      </fieldset>
""".format(release=all_discs[0]['release'],artist=all_discs[0]['artist'],year=all_discs[0]['year']))

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




if __name__ == '__main__':

    option_multiple = False
    option_freedb = False
    option_separator = " / "

    for arg in sys.argv[1:]:
        if arg=="-h":
            print(f"Usage: {sys.argv[0]} [-h] [-mX]\n\n"
                "  -h  this help\n"
                "  -m  multiple discs\n"
                "  -s  set separator between title and artist (default: -s' / ')\n"
                "  -f  print FreeDB entries\n")
            exit(1)
        elif arg=='-m':
            option_multiple = True
        elif arg=="-f":
            option_freedb = True
        else:
            print(f"Unknown argument {arg}", file=sys.stderr)
            exit(2)


    all_discs = []
    discno = 0
    while True:

        print(f"\nDisc {discno+1}\n--------------")

        d = discid.read()
        print(f"FreeDB: {d.freedb_id} MusicBrainz: {d.id}")
        print(f"MusicBrainz URL: {d.submission_url}")

        offsets = [t.offset for t in d.tracks]
        freedbDiscId = freedb.DiscID(offsets, d.seconds, d.last_track_num, d.seconds)
        md = freedb.perform_lookup(freedbDiscId, "gnudb.gnudb.org", 80)
        for item in md:
            print(f"{item['DISCID']}: {item['DTITLE']}")
            if (option_freedb):
                print(json.dumps(item, indent=2))

            # FIXME: currently always takes last item in list

            artist = ""
            release = item.get('DTITLE', "")
            pos = release.find(option_separator)
            if pos >= 0:
                artist = release[0:pos]
                release = release[pos+3:]
                if artist == "Various":
                    artist = "Various Artists"

            i = 0
            tracks = []
            while True:
                key = f"TTITLE{i}"
                if key in item:
                    tartist = ""
                    title = item[key]
                    pos = title.find(" / ")
                    if pos >= 0:
                        tartist = title[0:pos]
                        title = title[pos+3:]
                    tracks.append({'artist': tartist, 'title': title})
                else:
                    break
                i += 1

            disc_info = {
                'freedb_discid' : item.get('DISCID', ""),
                'release': release,
                'artist': artist,
                'year': item.get('DYEAR', ""),
                'tracks': tracks,
                'toc_str': d.toc_string,
            }
            print(disc_info)
            all_discs.append(disc_info)

        if not all_discs:
            print("Not found in gnudb")
            exit(3)



        if option_multiple == False:
            break

        answer = input("Press Enter to add another disc or anything else to stop: ")
        if (answer!=""):
            break

        discno += 1


    write_submit_file(all_discs)



