from flask_cors import CORS
from flask import Blueprint

api_bp = Blueprint('api_v1', __name__)

CORS(api_bp)

from .source import *