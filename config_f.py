TOKEN = ""  # token телеграм-бота

FOLDER_ID=''
IAM_TOKEN=''

MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 10  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога


MAX_USER_TTS_SYMBOLS = 1000
MAX_TTS_SYMBOLS = 200
MAX_USER_STT_BLOCKS = 12
MAX_USER_GPT_TOKENS = 2000

LOGS = 'logs.txt'  # файл для логов
PATH_TO_DB  = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]  # список с системным промтом

