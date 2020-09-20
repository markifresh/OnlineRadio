db_location = 'test2.sqlite'
exclude_radios = ['FIP_REGGAE', 'FIP_METAL']
url_api_open_radio = 'https://openapi.radiofrance.fr/v1/graphql'

djam_radio = {'id': 'DJAM',
              'url': 'https://www.djamradio.com',
              'tracks_request_url': 'https://www.djamradio.com/actions/retrieve.php'}


fip_radio = {'id': 'FIP',
             'url': 'https://www.fip.fr/',
             'tracks_request_url': url_api_open_radio}

all_environments = {
    "development": {
        "port": 5000,
        "debug": True,
        "swagger-url": "/api/swagger"},

    "production": {
        "port": 8080,
        "debug": False,
        "swagger-url": None}
}
