from datetime import datetime, timedelta


def get_date_range_list(start_date=None, end_date=None):
    if not end_date:
        end_date = datetime.now()
    else:
        if isinstance(end_date, str) and '-' in end_date:
            day, month, year = end_date.split('-')[:3]  # 06/09/2020
            day, month, year = int(day), int(month), int(year)
            end_date = datetime(year=year, month=month, day=day)

    if not start_date:
        start_date = end_date - timedelta(days=30)
    else:
        if isinstance(start_date, str) and '-' in start_date:
            day, month, year = start_date.split('-')[:3]  # 06/09/2020
            day, month, year = int(day), int(month), int(year)
            start_date = datetime(year=year, month=month, day=day)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    calendar = []
    day_current = start_date
    while day_current <= end_date:
        calendar.append(day_current)
        day_current += timedelta(days=1)

    return calendar

def sort_tracks_list(tracks_list):
    return sorted(tracks_list, key=lambda i: i['play_date'])