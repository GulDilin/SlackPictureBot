class MessageHandler:
    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel):
        self.channel = channel
        self.username = "picturebot"
        self.icon_emoji = ":dog"
        self.timestamp = ""
        self.reaction_task_completed = False
        self.pin_task_completed = False

    def get_files_num_error_message(self):
        return self._get_simple_message("Error", "You should pin only one file")

    def get_filetype_error_message(self):
        return self._get_simple_message("Error", "File should be *.zip* or *.7z*")

    def get_no_file_error_message(self):
        return self._get_simple_message("Error", "You should pin file")

    def get_upload_file_message(self):
        return self._get_simple_message("Oweeee", "You uploaded file. Please wait")

    def get_archive_res_error_message(self):
        return self._get_simple_message("Ou", "You put wrong files in archive.\n You need to put pic and json config")

    def get_json_error_message(self):
        return self._get_simple_message("Error", "Got invalid JSON file (width and height required")

    def get_no_such_command_message(self):
        return self._get_simple_message("Sorry", "No such command. Try hello")

    def get_message_hello(self, username):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                *self._get_hello_block(username),
                self.DIVIDER_BLOCK,
                *self._get_help_block(),
            ],
        }

    def _get_simple_message(self, caption, info):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                *self._get_task_block(caption, info)
            ],
        }

    def _get_hello_block(self, username):
        return self._get_task_block("Hello", username)

    def _get_help_block(self):
        return self._get_task_block("Commands",
                                    "Можешь напечатать команду resize и я изменю размер картинки. Принимаю .zip с картинкой в формате .png и .json с указанием размеров")

    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]
