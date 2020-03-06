#!/usr/bin/env python
# coding: utf-8
# Copyright 2020 Abram Hindle, Joseph Potentier
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect, url_for
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }


class World:
    def __init__(self):
        self.clear()

    def update(self, entity, key, value):
        entry = self.space.get(entity, dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data
        self.notify_all(entity, data)

    def clear(self):
        self.space = dict()
        self.subscribers = dict()

    def get(self, entity):
        return self.space.get(entity, dict())

    def world(self):
        return self.space

    def notify_all(self, entity, data):
        for subscriber in self.subscribers:
            self.subscribers[subscriber][entity] = data

    # Credit - Abram Hindle - https://github.com/abramhindle/CMPUT404-AJAX-Slides/blob/master/ObserverExample/server.py

    def add_subscriber(self, subscriber_id):
        self.subscribers[subscriber_id] = dict()

    def get_subscriber(self, subscriber_id):
        try:
            return self.subscribers[subscriber_id]
        except KeyError:
            self.add_subscriber(subscriber_id)
            return self.subscribers[subscriber_id]

    def clear_subscriber(self, subscriber_id):
        self.subscribers[subscriber_id] = dict()


# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}'


myWorld = World()

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.


def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])


@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return redirect(url_for('static', filename='index.html'))


@app.route("/entity/<entity>", methods=['POST', 'PUT'])
def update(entity):
    data = flask_post_json()
    myWorld.set(entity, data)
    '''update the entities via this interface'''
    return flask.jsonify(data)


@app.route("/world", methods=['POST', 'GET'])
def world():
    '''you should probably return the world here'''
    return flask.jsonify(myWorld.world())


@app.route("/entity/<entity>")
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    v = myWorld.get(entity)
    return flask.jsonify(v)


@app.route("/clear", methods=['POST', 'GET'])
def clear():
    myWorld.clear()
    return flask.jsonify(myWorld.world())


@app.route("/subscriber/<entity>", methods=['POST', 'PUT'])
def add_subscriber(entity):
    myWorld.add_subscriber(entity)
    return flask.jsonify(dict())


@app.route("/subscriber/<entity>")
def get_subscriber(entity):
    entity = entity.encode('utf-8')
    v = myWorld.get_subscriber(entity)
    myWorld.clear_subscriber(entity)
    return flask.jsonify(v)


if __name__ == "__main__":
    app.run()
