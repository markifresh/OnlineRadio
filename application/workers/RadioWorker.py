from application.radios.RadioDjam import Djam
from application.radios.RadioFip import Fip
from inspect import getmembers, isclass
from sys import modules


def create_radio(radio_name):
    radio_classes = getmembers(modules[__name__], isclass)

    for radio in radio_classes:
        r_name, r_class = radio
        if r_name.lower() in radio_name.lower():
            return r_class(radio_name)

    return None


def get_all_radios():
    result_dict = {}
    radio_classes = getmembers(modules[__name__], isclass)

    for radio in radio_classes:
        radio_class = radio[1]
        radios = radio_class.get_radios()

        if not radios['success']:
            return radios

        radios = radios['result']
        for radio_name in radios:
            result_dict[radio_name] = radios[radio_name]

    return {'success': True, 'result': result_dict}
