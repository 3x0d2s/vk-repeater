# -*- coding: utf8 -*-
from asyncio.log import logger
import logging
from environs import Env
#
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


def send_message(event, text=None, attachment_arg=None):
    vk_session.method(
        method='messages.send',
        values={'user_id': event.object.from_id,
                'message': text,
                'attachment': attachment_arg,
                'random_id': get_random_id(),
                }
    )


def repeat_photos(event):
    message_attachments = event.object.attachments

    counter_for_non_photos = 0
    attachment_arg = ""
    for message_attachment in message_attachments:
        media_type = message_attachment["type"]

        if media_type != "photo":
            counter_for_non_photos += 1
            continue

        owner_id = message_attachment["photo"]["owner_id"]
        photo_id = message_attachment["photo"]["id"]
        access_key = message_attachment["photo"]["access_key"]

        attachment_arg += f"{media_type}{owner_id}_{photo_id}_{access_key},"

    if counter_for_non_photos == len(message_attachments):
        text = "Отправь мне фотографии, чтобы я помог тебе! 😊"
        send_message(event=event, text=text)
    else:
        attachment_arg = attachment_arg[:-1]  # Обрезаем запятую в конце
        message_text = "Лови! 🥳"
        send_message(event=event,
                     text=message_text,
                     attachment_arg=attachment_arg
                     )

        user = vk_session.method(method='users.get',
                                 values={'user_id': event.object.from_id,
                                         'name_case': "gen",
                                         }
                                 )
        user_first_name = user[0]["first_name"]
        user_last_name = user[0]["last_name"]

        logger.info(
            msg=f"Обработаны фотографии {user_first_name} {user_last_name} (https://vk.com/id{event.object.from_id})."
        )


def main():
    # Главная функция инициализации и запуска бота.
    global vk_session, logger

    env = Env()
    env.read_env()
    TOKEN = env.str("TOKEN")
    GROUP_ID = env.str("GROUP_ID")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    vk_session = VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_user:

                message_text = event.object["text"]

                if message_text == "Начать":
                    start_text = "Привет! 😊\nЯ - чат-бот для добавления твоих фотографий в «Сохранёнки»!" \
                        "\nОтправь мне свои фотографии, а я перешлю их тебе, после чего ты сможешь добавить их к себе в альбом!"
                    send_message(event=event, text=start_text)
                    #
                elif len(event.object.attachments) == 0:
                    text = "Отправь мне фотографии, чтобы я помог тебе! 😊"
                    send_message(event=event, text=text)
                    #
                else:
                    repeat_photos(event=event)
                    #


if __name__ == '__main__':
    main()
