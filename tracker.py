import os
import json
import datetime
import time
import argparse

last_inspect = 0

CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')

_to_datetime = lambda seconds : datetime.datetime.fromtimestamp(seconds)
_to_seconds = lambda datime_object : time.mktime(datime_object.timetuple())

def get_files(parent_directory, ignore_list = None, ignore_function = None):
    if not get_files.exists(parent_directory):
        return []
    if not get_files.isdir(parent_directory):
        return [get_files.abspath(parent_directory)]

    output = []

    for file_name in os.listdir(parent_directory):
        full_path = get_files.join(parent_directory, file_name)
        if ignore_list:
            ignored = True
            for name in ignore_list:
                if name in full_path:
                    ignored = False
                    break

            if not ignored:
                continue

        if ignore_function and ignore_function(full_path):
            continue

        if get_files.isdir(full_path):
            output += get_files(full_path, ignore_list, ignore_function)
        else:
            output.append(get_files.abspath(full_path))

    return output


def get_last_modified(path):
    created =  os.path.getctime(path)
    modified = os.path.getmtime(path)

    return created, modified

def get_new(directory, ignore_list = None, ignore_function = None):
    output = []
    for file_name in get_files(directory, ignore_list, ignore_function):
        time_info = get_last_modified(file_name)

        created = time_info[0]
        modified = time_info[1]

        if created > last_inspect or modified > last_inspect:
            output.append(file_name)

    relpath = os.path.relpath
    return [relpath(path, directory) for path in output]

def update():
    global last_inspect
    last_inspect = time.time()

def get_config():
    if not os.path.isfile(CONFIG_FILE):
        return

    global last_inspect
    with open(CONFIG_FILE, 'r') as config_file:
        data = json.load(config_file)
        last_inspect = data['last_inspect']

def write_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'last_inspect' : last_inspect}, f)


get_files.join = os.path.join
get_files.exists = os.path.exists
get_files.isdir = os.path.isdir
get_files.abspath = os.path.abspath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Track files and directories for changes')
    parser.add_argument('-p', '--path', dest='path', default='.', help='path to look at', type = str)

    parser.add_argument('-n', '--no-update', dest='update', help='if inspect time should not be updated. Default to true unless this flag is present', action='store_false')
    parser.set_defaults(feature=True)

    parser.add_argument('-i', '--ignore', dest='ignores', nargs='*', type=str, help='List of string to ignore if present in the file path')

    args = parser.parse_args()
    ignores = args.ignores
    path = args.path
    should_update = args.update

    get_config()
    news = get_new(path, ignore_list = ignores)

    print ' '.join(news)

    if should_update:
        update()
    write_config()


