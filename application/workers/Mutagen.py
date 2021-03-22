from mutagen import File
from pathlib import Path

artist = ''
track = ''
track_format = ''
tracks_suffixes = ('.mp3', '.wma')

def check_object(obj):
    if isinstance(obj, str):
        obj = Path(obj)

    try:
        return {} if not obj.exists() else obj

    except:
        found_obj = None
        parent = obj.parent
        parent_dirs = [folder for folder in parent.iterdir() if folder.is_dir()]

        for folder in parent_dirs:
            if folder.name in obj.name:
                parent = folder

        objs = list(parent.rglob('**/*' + obj.suffix))
        target_objname= str(obj.name.encode())
        for res in objs:
            if res.name in target_objname:
                found_obj = res
                break

        return {} if not found_obj else found_obj


def check_file_name():
    pass


# replace with filepath or folderpath
def standardize_file_names(location):
    file = check_object(location)
    if not file:
        return (False, f'given path not exists')

    if file.is_dir():
        files = [file for file in list(file.rglob('**/*.*')) if file.suffix in tracks_suffixes]
    else:
        files = [file]

    result = []

    for file in files:
        mutagen_file = File(file, easy=True)
        artist = mutagen_file.get('artist', [''])[0]
        title = mutagen_file.get('title', [''])[0]
        new_name = file.name

        if artist and title and f'{artist} - ' not in file.name:
            file = Path(mutagen_file.filename)
            new_name = f'{artist} - {title}{file.suffix}'
            file.rename(file.parent / new_name)

        result.append((file.name != new_name, f"{file.name} --> {new_name}"))

    return result


def get_track(file, check=True):
    if check:
        file = check_object(file)
        if not file:
            return {}

    path = str(file.parent)
    common_name = file.name.rstrip(file.suffix).replace('_', ' ')
    folder = file.parent.name
    file_size = round(file.stat().st_size / (1024 * 1024), 2)
    file_format = file.suffix[1::]

    splited = common_name.split('-')
    artist = splited[0].strip()
    title = ('-'.join(splited[1:])).strip()

    track_dict = {
        'location': path,
        'common_name': common_name,
        'album_name': '',
        'album_year': '',
        'artist': artist,
        'title': title,
        'track_number': '',
        'genre': '',
        'size': file_size,
        'format': file_format,
        'bitrate': 0,
        'folder': folder
    }

    try:
        file = File(file, easy=True)
        if not file:
            return track_dict
    except:
        return track_dict


    artist = file.get('artist', [''])[0]
    title = file.get('title', [''])[0]

    if artist and title:
        common_name = f"{artist} - {title}"

    elif '-' in common_name:
        splited = common_name.split('-')
        artist = splited[0].strip()
        title = ('-'.join(splited[1:])).strip()

    track_dict = {
        'location': path,
        'common_name': common_name,
        'album_name': file.get('album', [''])[0],
        'album_year': file.get('date', [''])[0],
        'artist': artist,
        'title': title,
        'track_number': file.get('tracknumber', [''])[0],
        'genre': file.get('genre', [''])[0],
        'size': file_size,
        'format': file_format,
        'bitrate': file.info.bitrate // 1000,
        'folder': folder
    }


    return track_dict


def get_tracks_recursive():
    pass


def get_folder_tracks(folder):
    folder = folder if isinstance(folder, Path) else check_object(folder)
    if not folder:
        return {}

    files = list(folder.rglob('**/*.*'))
    return [get_track(file, False) for file in files if file.suffix in tracks_suffixes]





def modify_idv3_tags(tags_dict):
    pass
