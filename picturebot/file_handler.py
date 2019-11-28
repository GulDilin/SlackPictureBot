import requests
import subprocess
from message_handler import MessageHandler
import os
import re
import json
from image_resizer import resize_image

DOWNLOAD_DIR = "C:/Progs/SlackPictureBot/download_files/"
OUT_DIR = "C:/Progs/SlackPictureBot/output_images/"
UNPACK_DIR = "C:/Progs/SlackPictureBot/unpacked_files/"
PIC_TYPES = {"png", "jpeg", "jpg"}


# TODO загрузка файла по ссылке
def download(file_id, dir):
    token = os.environ['SLACK_BOT_TOKEN']

    # call file info to get url
    url = "https://slack.com/api/files.info"
    r = requests.get(url, {"token": token, "file": file_id})
    r.raise_for_status()
    response = r.json()
    assert response["ok"]
    file_name = response["file"]["name"]
    file_url = response["file"]["url_private"]
    print("Downloaded " + file_name)

    # download file
    r = requests.get(file_url, headers={'Authorization': 'Bearer %s' % token})
    r.raise_for_status()
    file_data = r.content  # get binary content

    # save file to disk
    with open(dir + file_name, 'w+b') as f:
        f.write(bytearray(file_data))
    print("Saved " + dir + file_name + " in current folder")

    return file_name


# TODO разорхивация файла
def unpack(file_path, destination_dir, new_dir):
    print(f'{file_path} is unpacking')
    try:
        os.mkdir(destination_dir + new_dir)
    except FileExistsError:
        pass
    subprocess.call(r'"C:\Program Files\7-Zip\7z.exe" x ' + file_path + ' -o' +
                    destination_dir + new_dir)


def check_files_num_in_pack(files_in_pack: list):
    if len(files_in_pack) != 2:
        return False

    pic_count = 0
    json_count = 0
    for file in files_in_pack:
        for type in PIC_TYPES:
            if re.match(r'.+\.' + type, file):
                pic_count += 1
        if re.match(r'.+\.json', file):
            json_count += 1

    return pic_count == 1 and json_count == 1


def get_json_file(files_in_pack: list):
    for file in files_in_pack:
        if re.match(r'.+\.json', file):
            return file


def get_pic_file(files_in_pack: list):
    for file in files_in_pack:
        for type in PIC_TYPES:
            if re.match(r'.+\.' + type, file):
                return file


def check_json(json_file_path):
    with open(json_file_path, "r") as read_file:
        data = json.load(read_file)

    try:
        return int(data['height']) and int(data['width'])
    except KeyError:
        return False
    except NameError:
        return False


def get_size(json_file_path):
    with open(json_file_path, "r") as read_file:
        data = json.load(read_file)
    return [int(data['width']), int(data['height'])]

def delete_files(path, files_in_pack):
    for file in files_in_pack:
        os.remove(path + file)

def handle_file(file_id, down_dir, unpk_dir, message_handler: MessageHandler):
    pic_file_name = ""
    # скачивание
    file_name = download(file_id, down_dir)

    rev = lambda s: s[::-1]
    new_dir = rev(rev(file_name).split(".", 2)[1])
    path = unpk_dir + new_dir + "/"
    # распаковка
    unpack(down_dir + file_name, unpk_dir, new_dir)
    files_in_pack = os.listdir(unpk_dir + new_dir)
    # проверка содержимого архива
    print(f'files_in_pack = {files_in_pack}')

    if not check_files_num_in_pack(files_in_pack):
        delete_files(path, files_in_pack)
        return "num_file_err"

    json_file_path = path + get_json_file(files_in_pack)
    print(f'files_in_pack = {files_in_pack}')

    pic_file_name = get_pic_file(files_in_pack)
    pic_file_path = path + pic_file_name

    if not check_json(json_file_path):
        delete_files(path, files_in_pack)
        return "json_err"

    size = get_size(json_file_path)
    print(f'picture path = {pic_file_path}')
    resize_image(pic_file_path, OUT_DIR + pic_file_name, size)

    delete_files(path, files_in_pack)

    return OUT_DIR + pic_file_name


def handle_file_with_def_dirs(file_id, message_handler: MessageHandler):
    return handle_file(file_id, DOWNLOAD_DIR, UNPACK_DIR, message_handler)
