import os
import logging
import traceback
import slack
from message_creator import MessageCreator
from commands.resize import resize_image
from commands.say_hello import say_hello
from commands.help import say_help

# id бота, появляется после его старта
bot_id = None

# константы допустимых команд
COMMANDS_NAMES = ("hello", "resize", "help")
COMMANDS_FUNCS = (say_hello, resize_image, say_help)
COMMANDS = dict(zip(COMMANDS_NAMES, COMMANDS_FUNCS))


def handle_command(command, channel, web_client, data):
    message = None
    message_creator = MessageCreator(channel)
    command = command.replace(f'<@{bot_id.lower()}>', '').split()[0]

    if command not in COMMANDS_NAMES:
        message = message_creator.get_no_such_command_message()
    else:
        message = COMMANDS[command](data=data, web_client=web_client, message_creator=message_creator)

    if message is not None:
        web_client.chat_postMessage(**message)

    return message


@slack.RTMClient.run_on(event='member_joined_channel')
def new_user_added(**payload):
    # поздороваться с новым пользователем
    data = payload['data']
    web_client = payload['web_client']
    channel_id = data['channel']
    message_creator = MessageCreator(channel_id)
    web_client.chat_postMessage(message_creator.get_message_hello(data['user']))


@slack.RTMClient.run_on(event='message')
def parse_command(**payload):
    data = payload['data']
    web_client = payload['web_client']
    # идентификатор канала
    channel_id = data['channel']
    # сообщение пользователя
    text = data.get('text', []).lower()

    if f'@{bot_id.lower()}' in text:
        print("\n" + "-" * 10)
        print(text + "\n")
        handle_command(command=text, channel=channel_id, web_client=web_client, data=data)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    isrun = False
    while True:
        try:
            print("\n\n----------------\nЗапуск Picture Bot")
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
        except TimeoutError:
            print("Проблемы с сетью")
        except BaseException:
            print("Что-то не так. Перезапускаюсь")
            print('Ошибка:\n', traceback.format_exc())
