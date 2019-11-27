import os
import time
import re
import logging
import ssl as ssl_lib
import slack
import certifi
from message_handler import MessageHandler

# id бота, появляется после его старта
bot_id = None

# константа допустимых команд
COMMANDS = {"hello", "resize"}
FILE_TYPES_AR = {"zip", "7z"}
FILE_TYPES_FILES = {"png", "jpeg"}


@slack.RTMClient.run_on(event='message')
def say_hello(**payload):
    data = payload['data']
    web_client = payload['web_client']
    text = data.get('text', []).lower()
    text_message = text.replace(f'<@{bot_id.lower()}>', '')
    if 'hello' in text_message or (f'@{bot_id.lower()}' in text and text_message not in COMMANDS):
        channel_id = data['channel']
        user = data['user']
        message_handler = MessageHandler(channel_id)

        if 'hello' in text:
            message = message_handler.get_message_payload(f"<@{user}>")
        else:
            message = message_handler.get_no_such_command_message()

        web_client.chat_postMessage(**message)


# получение url файла
@slack.RTMClient.run_on(event='file_shared')
def say_file_loaded(**payload):
    print("I found file")
    print(payload)

    data = payload['data']
    file_id = data['file_id']
    web_client = payload['web_client']
    channel_id = data['channel_id']
    message_handler = MessageHandler(channel_id)

    file_info = web_client.files_info(token=slack_token, file=file_id)
    file_info = file_info['file']
    url = file_info['url_private']
    file_type = file_info['filetype']

    if file_type not in FILE_TYPES_AR:
        message = message_handler.get_filetype_error_message()
    else:
        message = message_handler.get_upload_file_message()

    print(url)

    web_client.chat_postMessage(**message)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    isrun = False
    try:
        print("Запуск Picture Bot")
        slack_token = os.environ["SLACK_BOT_TOKEN"]
        rtm_client = slack.RTMClient(token=slack_token)
        slack_client = slack.WebClient(token=slack_token)
        bot_id = slack_client.api_call("auth.test")["user_id"]
        print(f"Picture Bot id={bot_id} запущен")
        isrun = True
        rtm_client.start()
    except KeyError:
        if isrun:
            print("Бот упал")
            print(KeyError.__str__)
        else:
            print("Невозможно запустить. Не задана переменная окружения SLACK_BOT_TOKEN")
