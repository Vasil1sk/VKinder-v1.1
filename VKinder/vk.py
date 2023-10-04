import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import json
from random import randrange

# Получаем токены
with open("token.json") as f:
    data = json.load(f)
    user_token = data["user_token"]
    bot_token = data["bot_token"]

# Присваиваем токены
vk_user = vk_api.VkApi(token=user_token)
vk_bot = vk_api.VkApi(token=bot_token)
longpoll = VkLongPoll(vk_bot)

# Функция для отправки сообщения с вложениями
def write_msg(user_id, message, attachment=None, keyboard=None):
    vk_bot.method("messages.send", {"user_id": user_id, "message": message, "attachment": attachment,
                                      "random_id": randrange(10 ** 7), "keyboard": keyboard})


# Функция для получения информации о пользователе
def get_user_info(user_id):
    response = vk_user.method("users.get", {"user_ids": user_id, "fields": "sex, city, bdate"})
    user_info = response[0]
    return user_info

# Функция, запрашивающая город, указанный в вконтакте, для поиска пары
def get_city_name(user_id):
    write_msg(user_id, f'Введите город искомой пары: ', None)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            city_name = event.text
            return city_name

# Функция, запрашивающая возраст для поиска пары
def get_age(user_id):
    write_msg(user_id, f'Введите возраст искомой пары: ', None)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            age = event.text
            return age

# Функция для поиска подходящей пары
def search(user_info, city_name=None, age=None, offset=0):
    sex = user_info.get("sex")
    city_id = vk_user.method("database.getCities", {"q": city_name,
                                                    "need_all": 1})
    found_users = []
    response = vk_user.method("users.search", {"count": 3,
                                               "sex": 1 if sex == 2 else 2,
                                               "city_id": city_id["items"][0]["id"],
                                               "age_from": int(age) - 1,
                                               "age_to": int(age) + 1,
                                               "has_photo": 1,
                                               "offset": offset})
    for user in response["items"]:
        if user["is_closed"] == False:
            found_users.append(user)
    return found_users

# Функция, получающая фотографии найденной пары
def get_user_photos(user_id):
    response = vk_user.method("photos.get", {
                                                "owner_id": user_id,
                                                "album_id": "profile",
                                                "extended": "likes"})
    photos = response.get("items")
    sorted_photos = sorted(photos, key=lambda x: x["likes"]["count"], reverse=True)
    most_liked_photos = sorted_photos[:3]
    return [f'photo{photo["owner_id"]}_{photo["id"]}' for photo in most_liked_photos]

# Функция для форматирования информации о паре
def format_user_info(user):
    first_name = user["first_name"]
    last_name = user["last_name"]
    profile_link = f"https://vk.com/id{user['id']}"
    return f"{first_name} {last_name}\nПрофиль: {profile_link}"