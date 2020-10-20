from datetime import datetime, timedelta
from flask import abort, request
from flask_restx import reqparse, inputs

date_range_req = reqparse.RequestParser()
current_year = str(datetime.now().year)
date_range_req.add_argument('start',
                            type=inputs.regex(f'^(0[1-9]|1[0-9]|2[0-9]|3[0-1])(-)(0[1-9]|1[0-2])(-){current_year}+$'),
                            help=f'use format: dd-mm-{current_year}',
                            required=True)

date_range_req.add_argument('end',
                            type=inputs.regex(f'^(0[1-9]|1[0-9]|2[0-9]|3[0-1])(-)(0[1-9]|1[0-2])(-){current_year}+$'),
                            help=f'use format: dd-mm-{current_year}',
                            required=True)

limit_req = reqparse.RequestParser()
limit_req.add_argument('limit', type=int, required=False, default=50, help='results limit')

from_id_req = reqparse.RequestParser()
from_id_req.add_argument('from_id', type=int, required=False, default=0, help='data id from')

radio_req = reqparse.RequestParser()
radio_req.add_argument('radio_name', type=str, required=True)



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

