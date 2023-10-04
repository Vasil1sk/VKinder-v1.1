from vk import *
from vk_db import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Активируем бота
def start_bot():
    users_list = [] # list с информацией о пользователе
    current_user_index = 0  # Индекс текущей пары в списке найденных пар
    offset = 0 # Смещение относительно первого найденного пользователя для выборки определенного подмножества, он же обход ограничения count поиска
    # Бот начинает работу
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request == "привет":
                    user_info = get_user_info(event.user_id)
                    add_user(user_info)
                    keyboard = VkKeyboard()
                    keyboard.add_button("Ввести данные", VkKeyboardColor.PRIMARY)
                    keyboard.add_button("Завершить поиск", VkKeyboardColor.PRIMARY)
                    keyboard.add_button("Найти пару", VkKeyboardColor.PRIMARY)
                    write_msg(event.user_id, "Здравствуйте, я бот VKinder. "
                                             "Я помогу найти вам пару в социальной сети ВКонтакте! "
                                             "Для начала работы введите данные для поиска, нажав 'Ввести данные'.\n"
                                             "Если вы хотите завершить поиск, то нажмите 'Завершить поиск'.", keyboard=keyboard.get_keyboard())
                elif request == "завершить поиск":
                    write_msg(event.user_id, "До свидания, было приятно с вами работать!")
                elif request == "ввести данные":
                    city_name = get_city_name(event.user_id)
                    age = get_age(event.user_id)
                    write_msg(event.user_id, "Отлично, данные получены! Чтобы найти себе пару "
                                             "нажмите 'Найти пару' "
                                             "Если вы хотите ввести новые данные поиска, "
                                             "то повторно нажмите  'Ввести данные'.")
                elif request == "найти пару":
                    keyboard.add_button("Дальше", VkKeyboardColor.PRIMARY)
                    keyboard.add_button("Добавить", VkKeyboardColor.PRIMARY)
                    found_users = search(user_info, city_name, age)
                    add_users(found_users, event.user_id)
                    if found_users:
                        users_list = found_users
                        current_user_index = -1
                        while current_user_index != 2:
                            current_user_index += 1
                            if users_list[current_user_index]["id"] not in check_users():
                                user_photos = get_user_photos(users_list[current_user_index]["id"])
                                write_msg(event.user_id, format_user_info(users_list[current_user_index]), ",".join(user_photos))
                                write_msg(event.user_id, "Если вы хотите добавить пару в избранное, то нажмите 'Добавить'\n"
                                                         "Чтобы продолжить поиск нажмите 'Дальше'.", keyboard=keyboard.get_keyboard())
                        else:
                            write_msg(event.user_id, "К сожалению, не найдено подходящей пары")
                elif request == "дальше":
                    offset += 3
                    found_users = search(user_info, city_name, age, offset=offset)
                    add_users(found_users, event.user_id)
                    if found_users:
                        users_list = found_users
                        new_user_index = -1
                        while new_user_index != len(users_list) - 1:
                            new_user_index += 1
                            if users_list[new_user_index]["id"] not in check_users():
                                user_photos = get_user_photos(users_list[new_user_index]["id"])
                                write_msg(event.user_id, format_user_info(users_list[new_user_index]),
                                          ",".join(user_photos))
                                write_msg(event.user_id,
                                          "Если вы хотите добавить пару в избранное, то нажмите 'Добавить'\n"
                                          "Чтобы продолжить поиск нажмите 'Дальше'.")
                    else:
                        write_msg(event.user_id, "К сожалению, не найдено подходящей пары")
                elif request == "добавить":
                    keyboard.add_line()
                    keyboard.add_button("Избранное", VkKeyboardColor.PRIMARY)
                    keyboard.add_button("1", VkKeyboardColor.PRIMARY)
                    keyboard.add_button("2", VkKeyboardColor.PRIMARY)
                    keyboard.add_button("3", VkKeyboardColor.PRIMARY)
                    write_msg(event.user_id, "Какую пару вы хотите добавить в избранное?", keyboard=keyboard.get_keyboard())
                    write_msg(event.user_id, "Выберете пару и нажмите соотвествующее ей число.")
                # Какую пару добавить 1 2 3. Если 3, то индекс неизменный, если 2, то -1, если 3, то -2
                elif request == "1":
                    if users_list:
                        add_favorite(users_list[current_user_index - 2])
                        write_msg(event.user_id, "Пара добавлена в избранное. "
                                                     "Чтобы увидеть список избранных пар "
                                                     "нажмите 'избранное'.")
                    else:
                        write_msg(event.user_id, "Не удалось добавить пару в избранное.")
                elif request == "2":
                    if users_list:
                        add_favorite(users_list[current_user_index - 1])
                        write_msg(event.user_id, "Пара добавлена в избранное. "
                                                     "Чтобы увидеть список избранных пар "
                                                     "нажмите 'избранное'.")
                    else:
                        write_msg(event.user_id, "Не удалось добавить пару в избранное.")
                elif request == "3":
                    try:
                        if users_list:
                            add_favorite(users_list[current_user_index])
                            write_msg(event.user_id, "Пара добавлена в избранное. "
                                                         "Чтобы увидеть список избранных пар "
                                                         "нажмите 'избранное'.")
                    except IndexError:
                        write_msg(event.user_id, "Не удалось добавить пару в избранное.")
                elif request == "избранное":
                        write_msg(event.user_id, f"{show_favorites()}", None)
                else:
                    write_msg(event.user_id, "Не понял вашего ответа...")

if __name__ == "__main__":
    start_bot()