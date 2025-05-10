from flask import Blueprint

admin= Blueprint('admin',__name__)

from Resort.admin import routes