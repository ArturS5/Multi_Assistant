TOKEN = "7083933588:AAG1u27GGEeIXWmN0CxW9EaEJX94FMQYPUM"  # token телеграм-бота

FOLDER_ID='b1gs35092smnokbou6me'
IAM_TOKEN='t1.9euelZqNmZTNi86KmsuWm8rGjIuXi-3rnpWaipKLjJ6cnM-TjI7PkYyJjsjl8_cOPwdO-e8NWj15_N3z905tBE757w1aPXn8zef1656VmouOmZfGy8zHzcrJlcvInc3G7_zF656VmouOmZfGy8zHzcrJlcvInc3GveuelZqQkIvKjM7Mko-OkJnLl46Vk7XehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.Hv11fEs3CjsGvJRy8zLdaI2Qi_T-Mn2HtixajgujfcNhpcYKYr3DHvz-2wqiVUbvg6DlbLrD_nSv1pvG50POBQ'

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

