#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from os.path import isfile
from configparser import ConfigParser
from lxml import objectify
from flask import Flask, jsonify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


song_attributes = ["title", "uuid", "lyrics", "composer", "authorText", "authorTranslation", "publisher",
                   "additionalCopyrightNotes", "language", "songNotes", "tonality", "chordSequence"]


def read_xml(filename):
    with open(filename, 'rb') as reader:
        xml_content = reader.read()
        return objectify.fromstring(xml_content)


def attr_present(song, attribute):
    return hasattr(song, attribute) and not song[attribute] is None and not song[attribute].text is None


def txt(song, attribute):
    if attr_present(song, attribute):
        return song[attribute].text
    else:
        return None


def add_txt(song, attribute, result):
    if attr_present(song, attribute):
        result[attribute] = song[attribute].text


app = Flask(__name__)


@app.route("/")
def root():
    return "use /song for an overview or /song/UUID for the details of a specific song"


@app.route("/song")
def overview():
    result = []
    for song in xml.song:
        result.append({"title": txt(song, "title"), "uuid": txt(song, "uuid")})
    return jsonify(result)


@app.route("/song/<uuid>")
def details(uuid):
    for song in xml.song:
        if txt(song, "uuid") == uuid:
            result = {}
            for attribute in song_attributes:
                add_txt(song, attribute, result)
            return result
    return "not found"


if __name__ == "__main__":
    if not isfile("config.ini"):
        print("config.ini not found - maybe you didn't copy (and customize) "
              "the file config-template.ini to config.ini yet?")
        exit(1)

    config = ConfigParser()
    config.read("config.ini")

    xml = None

    def load_xml():
        global xml
        xml = read_xml(config["INPUT"]["file"])

    load_xml()

    class ReloadEventHandler(FileSystemEventHandler):
        def on_modified(self, event):
            load_xml()

        def on_created(self, event):
            load_xml()

    observer = Observer()
    observer.schedule(ReloadEventHandler(), config["INPUT"]["file"])
    observer.start()

    app.run()
