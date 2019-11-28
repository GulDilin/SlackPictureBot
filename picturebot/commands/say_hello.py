def say_hello(web_client, data, message_creator):
    user = data['user']
    message = message_creator.get_message_hello(f"<@{user}>")
    return message
