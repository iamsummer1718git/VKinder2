import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from data_store import add_viewed, insert_viewed, add_favourite, show_favourite
from config import comunity_token, acces_token
from core import VkTools
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class BotInterface:

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.keyboard = self.current_keyboard()


    @staticmethod
    def current_keyboard():
        VK_kb = VkKeyboardColor
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Привет', color=VK_kb.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Поиск', color=VK_kb.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Лайк!', color=VK_kb.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Просмотреть избранное', color=VK_kb.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('Очистить избранное', color=VK_kb.NEGATIVE)


        return keyboard.get_keyboard()


    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'keyboard': self.keyboard,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):
        global photo, user
        longpoll = VkLongPoll(self.interface)
        cnt = 0
        city_name_in = 'город '
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    backslash = '\n'
                    self.message_send(event.user_id, f'Здравствуй {self.params["name"]}, давай найдем тебе пару?')
                    self.message_send(event.user_id, f'Следуй моим инструкциям, чтобы у нас все получилось!{backslash}Ecли бот не запрашивает дополнительную информацию, можешь нажимать поиск!')
                    if self.params['bdate'] is None and self.params['city'] is None:
                        self.message_send(event.user_id, f'Укажите вашу дату рождения в формате ДД.ММ.ГГГГ, а затем в другом сообщении город в формате "город Москва"')
                    elif self.params['bdate'] is None:
                        self.message_send(event.user_id, f'Укажите вашу дату рождения в формате ДД.ММ.ГГГГ')
                    elif self.params['city'] is None:
                        self.message_send(event.user_id, f'Укажите ваш город, например: город Москва')
                elif len(command.split('.')) == 3:
                    self.params['bdate'] = command
                    self.message_send(event.user_id, f'Спасибо, теперь если указан город, нажмите Поиск')
                elif city_name_in in command:
                    city_name = command[6:]
                    city_user = self.api.get_city(city_name)
                    self.params['city'] = city_user
                    self.message_send(event.user_id, f'Спасибо, теперь нажмите поиск!')
                elif command == 'поиск':
                    users = self.api.serch_users(self.params)
                    user = users.pop(cnt)
                    while insert_viewed(user["id"]):
                        cnt += 1
                        user = users.pop(cnt)
                    photos_user = self.api.get_photos(user['id'])
                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{user["id"]}_{photo["id"]},'
                        if num == 2:
                            break
                    self.message_send(event.user_id,
                                    f'Встречайте {user["name"]}, vk.com/id{user["id"]}',
                                    attachment=attachment
                                    )
                    add_viewed(user["id"], event.user_id)
                elif command == 'лайк!':
                    print(add_favourite(user['id'], event.user_id))
                    self.message_send(event.user_id, f'Пользователь добавлен в избранные!')
                elif command == 'пока':
                    self.message_send(event.user_id, f'До свидания! Надеюсь, что я Вам помог')
                elif command == 'избранное':
                    res = show_favourite(event.user_id)
                    id_list = []
                    for id in res:
                        id_list.append(id[0])
                    for x in id_list:
                        y = self.api.get_profile_info(x)
                        y = y['name']
                        x = f'Возвращаемся к {y} vk.com/id' + str(x)
                        self.message_send(event.user_id, f'{x}')
                else:
                    self.message_send(event.user_id, f'Извините, но такой команды я не знаю. Пользуйтесь кнопками бота, чтобы у нас получилось понять друг друга!')





if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
