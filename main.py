from flask import Flask, render_template, request

import os
import openai
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from app import flask_app
import psycopg2
from psycopg2 import sql
import warnings

from openai import OpenAI
#https://github.com/openai/openai-python/discussions/742





app = flask_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)