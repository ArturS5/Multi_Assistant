import logging
from telebot import TeleBot
from validators_f import *  # модуль для валидации
from yandex_gpt_f import *  # модуль для работы с GPT
from config_f import *      # подтягиваем константы из config файла
from database_f import *    # create_database, add_message, select_n_last_messages
from speechkit_f import *   # text_to_speech, speech_to_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=LOGS,
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)

create_database()

bot = TeleBot(TOKEN)

#/start, /help
@bot.message_handler(commands=['start', 'help'])
def help_msg(message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст")


#/debug
@bot.message_handler(commands=['debug'])
def debug(message):
    with open(LOGS, "rb") as f:
        bot.send_document(message.chat.id, f)


#/tts
@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id,
                     'Отправь следующим сообщеним текст, чтобы я его озвучила!')
    bot.register_next_step_handler(message, tts)

def tts(message):
    user_id = message.from_user.id
    try:
        text = message.text
        tts_symbols, error_message = is_tts_symbol_limit(message=message, text=text)
        if error_message:
            bot.send_message(user_id, error_message)
            return
        add_message(user_id=user_id, full_message=[text, 'test', 0, tts_symbols, 0])
        status_tts, voice_response = text_to_speech(text)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, "Возникла ошибка", reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


#/stt
@bot.message_handler(commands=['stt'])
def stt_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознала!')
    bot.register_next_step_handler(message, stt)

# Переводим голосовое сообщение в текст после команды stt
def stt(message):
    user_id = message.from_user.id
    try:
        if not message.voice:
            bot.send_message(user_id, 'Неверный тип данный. Повторите попытку, введя /stt снова')
            return
        stt_blocks, error_message = is_stt_block_limit(message, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return
        add_message(user_id=user_id, full_message=[stt_text, 'test', 0, 0, stt_blocks])
        bot.send_message(user_id, stt_text)
    except Exception as e:
        logging.error(e)
        bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение, введя /stt снова")


#/voice
def handle_voice(message):
    user_id = message.from_user.id
    try:
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return
        stt_blocks, error_message = is_stt_block_limit(message,
                                                       message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return
        add_message(user_id=user_id,
                    full_message=[stt_text, 'user', 0, 0, stt_blocks])
        last_messages, total_spent_tokens = select_n_last_messages(user_id,
                                                                   COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages,
                                                             total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer
        tts_symbols, error_message = is_tts_symbol_limit(message=message,
                                                         text=answer_gpt)
        add_message(user_id=user_id,
                    full_message=[answer_gpt, 'assistant', total_gpt_tokens,
                                  tts_symbols, 0])
        if error_message:
            bot.send_message(user_id, error_message)
            return
        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response,
                           reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt,
                             reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)
        bot.send_message(user_id,
                         "Не получилось ответить. Попробуй записать другое сообщение")


# /text
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        # ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя (если пользователь новый)
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)  # мест нет =(
            return

        # БД: добавляем сообщение пользователя и его роль в базу данных
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        # ВАЛИДАЦИЯ: считаем количество доступных пользователю GPT-токенов
        # получаем последние 4 (COUNT_LAST_MSG) сообщения и количество уже потраченных токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        # получаем сумму уже потраченных токенов + токенов в новом сообщении и оставшиеся лимиты пользователя
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, error_message)
            return

        # GPT: отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        # GPT: обрабатываем ответ от GPT
        if not status_gpt:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, answer_gpt)
            return
        # сумма всех потраченных токенов + токены в ответе GPT
        total_gpt_tokens += tokens_in_answer

        # БД: добавляем ответ GPT и потраченные токены в базу данных
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)
        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю текстом
    except Exception as e:
        logging.error(e)  # если ошибка — записываем её в логи
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


# обрабатываем все остальные типы сообщений
@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")

bot.polling()
