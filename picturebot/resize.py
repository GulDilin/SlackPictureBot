import file_handler

FILE_TYPES_AR = {"zip", "7z"}


def do_command(data, web_client, message_handler):
    message = None
    try:
        files = data['files']
        print(f"files = {files}")

        if len(files) == 1:
            file_info = files[0]
            file_name = str(file_info['name'])
            file_id = file_info['id']
            rev = lambda string: string[::-1]
            file_type = rev(rev(file_name).split(".")[0])
            print(f'file type = {file_type}')
            url = file_info['url_private']

            if file_type not in FILE_TYPES_AR:
                # ошибка формата архива
                message = message_handler.get_filetype_error_message()
            else:
                # скачивание в случае успеха
                web_client.chat_postMessage(**message_handler.get_upload_file_message())
                pic_file_path = file_handler.handle_file_with_def_dirs(file_id, message_handler)

                if pic_file_path == "num_file_err":
                    return message_handler.get_archive_res_error_message()

                if pic_file_path == "json_err":
                    return message_handler.get_json_error_message()

                print(f"res_pic = {pic_file_path}")
                response = web_client.files_upload(
                    channels=data['channel'],
                    file=pic_file_path)
                assert response["ok"]

        else:
            # больше одного файла прикреплено
            message = message_handler.get_files_num_error_message()

    except KeyError:
        # нет прикрепленных файлов
        message = message_handler.get_no_file_error_message()
    return message
