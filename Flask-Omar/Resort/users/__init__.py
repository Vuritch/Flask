from flask import Blueprint

users= Blueprint('users',__name__)

from Resort.users import routes