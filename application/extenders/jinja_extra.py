from flask import  Blueprint
from config import read_date_time_format

jinja_extra = Blueprint('jinja_extra', __name__)


@jinja_extra.app_template_filter()
def format_date(somedate):
    return somedate.strftime(read_date_time_format)