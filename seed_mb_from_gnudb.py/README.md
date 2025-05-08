# Seed MusicBrainz from gnudb/FreeDB

Small script that identifies the current CD in the CD drive, retreives the track
information from the [Global Network Universal Database (gnudb)](https://gnudb.org)
and prepares a .html file to submit this data to [MusicBraninz](https://muscicbrainz.org).

## Installation

    python -m venv .venv
    . .venv/bin/activate
    pip install discid
