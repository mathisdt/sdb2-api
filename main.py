#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from os.path import isfile
from configparser import ConfigParser
from lxml import objectify
from flask import Flask, jsonify


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


# WORKAROUND from https://youtrack.jetbrains.com/issue/PY-49984, use to debug with PyCharm 2021.2.0 and below:
#app = Flask(__name__, instance_path="/{project_folder_abs_path}/instance")
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
            add_txt(song, "title", result)
            add_txt(song, "uuid", result)
            add_txt(song, "lyrics", result)
            add_txt(song, "composer", result)
            add_txt(song, "authorText", result)
            add_txt(song, "authorTranslation", result)
            add_txt(song, "publisher", result)
            add_txt(song, "additionalCopyrightNotes", result)
            add_txt(song, "language", result)
            add_txt(song, "songNotes", result)
            add_txt(song, "tonality", result)
            add_txt(song, "chordSequence", result)
            return result
    return "not found"


if __name__ == "__main__":
    if not isfile("config.ini"):
        print("config.ini not found - maybe you didn't copy (and customize) "
              "the file config-template.ini to config.ini yet?")
        exit(1)

    config = ConfigParser()
    config.read("config.ini")

    xml = read_xml(config["INPUT"]["file"])

    app.run()
