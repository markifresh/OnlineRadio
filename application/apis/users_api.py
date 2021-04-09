from application.db_models import track
from flask_restx import Namespace, Resource, fields, reqparse, inputs
from flask import request
from application.schema_models.tracks_schemas import *
from datetime import datetime


users_api = Namespace('Users', description='Methods of Users')