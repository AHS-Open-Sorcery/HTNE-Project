from flask import Flask, render_template, request
from helpers import *
from dataRetrieval import *
from login.__init__ import *


@app.route("/create-post")
def create_post():
	return "create-post"


@app.route("/display-posts")
def display():
	return "display-post"


