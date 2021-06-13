from application.music_services.Spotify import Spotify
from application.music_services.Deezer import Deezer
from inspect import getmembers, isclass
from sys import modules


def get_service(name, token=''):
    name = name.lower()
    results = getmembers(modules[__name__], isclass)
    for result in results:
        if result[0].lower() == name:
            return result[1](token)
    return None

def get_all_services():
    result = getmembers(modules[__name__], isclass)
    result = [ms[1]() for ms in result]
    # result = [(ms[0].lower(), ms[1]) for ms in result]
    return {'success': True, 'result': result}


def find_track(track, service_objects=get_all_services()['result']):
    if not isinstance(service_objects, list):
        service_objects = [service_objects]
    search_result = {'services': {}, 'rank': 0}
    for service in service_objects:
        service_name = service.__class__.__name__.lower()
        result = service.find_track(track)
        if result['success']:
            search_result['services'][service_name] = result['result']['id']
            if service_name == 'deezer':
                search_result['rank'] = result['result']['rank']

    return search_result