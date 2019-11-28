import os
import logging
import traceback
import slack
from message_handler import MessageHandler
import resize


# id бота, появляется после его старта
bot_id = None

# константа допустимых команд
COMMANDS = {"hello", "resize"}



@slack.RTMClient.run_on(event='message')
def parse_command(**payload):
    # переменная для сообщения
    message = None

    data = payload['data']
    web_client = payload['web_client']
    text = data.get('text', []).lower()
    text_message = text.replace(f'<@{bot_id.lower()}>', '')  # сообщение пользователя (команда)

    # инициализация обработчика сообщений в канале
    channel_id = data['channel']
    message_handler = MessageHandler(channel_id)

    # если нет такой команды
    if f'@{bot_id.lower()}' in text and text_message not in COMMANDS:
        message = message_handler.get_no_such_command_message()

    # команда приветствия
    if 'hello' in text_message or ():
        user = data['user']
        message = message_handler.get_message_hello(f"<@{user}>")

    # команда изменения размера
    elif 'resize' in text_message:
        message = resize.do_command(data, web_client, message_handler)

    if message is not None:
        web_client.chat_postMessage(**message)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    isrun = False
    try:
        print("Запуск Picture Bot")
        slack_token = os.environ["SLACK_BOT_TOKEN"]
        slack_team_token = os.environ["SLACK_TEAM_TOKEN"]
        rtm_client = slack.RTMClient(token=slack_token)
        slack_client = slack.WebClient(token=slack_token)
        bot_id = slack_client.api_call("auth.test")["user_id"]
        print(f"Picture Bot id={bot_id} запущен")
        isrun = True
        rtm_client.start()
    except KeyError:
        if isrun:
            print("Бот упал")
            print('Ошибка:\n', traceback.format_exc())
        else:
            print("Невозможно запустить. Не задана переменная окружения SLACK_BOT_TOKEN")
