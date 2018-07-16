#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world!"

@app.route("/tomas")
def tomas():
    return "Hello, Tomas!"

@app.route("/Sam")
def Sam():
    return "Hello, Sam!"
