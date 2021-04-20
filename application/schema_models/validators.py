from datetime import datetime, timedelta
from flask import abort, request
from flask_restx import reqparse, inputs
from config import date_format

current_year = str(datetime.now().year)
# https://regexr.com/
# date_regx_format = f'^(0[1-9]|1[0-9]|2[0-9]|3[0-1])(-)(0[1-9]|1[0-2])(-){current_year}+$'
# time_regx_format = f'^([01]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])+$'
date_regx_format = f'^(0[1-9]|1[0-9]|2[0-9]|3[0-1])-(0[1-9]|1[0-2])-{current_year}+$'   # 01-01-2021
time_regx_format = f'^([01]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])+$'                  # 00:00:00
datetime_regx_format = date_regx_format.replace('+$', ' ') + time_regx_format.replace('^', '')

date_range_req = reqparse.RequestParser()
date_range_req.add_argument('start',
                            type=inputs.regex(date_regx_format),
                            help=f'use format: dd-mm-{current_year}',
                            required=True)

date_range_req.add_argument('end',
                            type=inputs.regex(date_regx_format),
                            help=f'use format: dd-mm-{current_year}',
                            required=True)

limit_req = reqparse.RequestParser()
limit_req.add_argument('limit', type=int, required=False, default=50, help='results limit')

from_id_req = reqparse.RequestParser()
from_id_req.add_argument('from_id', type=int, required=False, default=0, help='data id from')

radio_req = reqparse.RequestParser()
radio_req.add_argument('radio_name', type=str, required=True)

account_id = reqparse.RequestParser()
account_id.add_argument('account_id', type=str, required=True)



def validate_date_range(start='', end=''):
    if not (start and end):
        start = request.args.get('start', '')
        end = request.args.get('end', '')

    if (not start) or (not end):
        abort(400, 'Start or end is missing')

    start = datetime.strptime(start, '%d-%m-%Y')
    end = datetime.strptime(end, '%d-%m-%Y') + timedelta(hours=23, minutes=59)

    if end < start:
        abort(400, 'End date is less than start')

    return start, end


def validate_date(date):
    try:
        date = datetime.strptime(date, date_format)

    except:
        abort(400, f'dateformat is different to: {date_format}')

    return date


def validate_date_range_post(start, end):
    try:
        start = datetime.strptime(start, '%d-%m-%Y')
        end = datetime.strptime(start, '%d-%m-%Y')
    except:
        abort(400, f'dateformat is different to: {date_format}')

    return start, end

