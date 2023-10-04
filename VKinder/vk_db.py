from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import create_tables, drop_tables, User, User_search_data, White_list
from sqlalchemy.exc import IntegrityError, InvalidRequestError, PendingRollbackError
from vk import write_msg

# База данных
DSN = "postgresql://postgres:ПарольБД@localhost:5432/ИмяБД"

engine = create_engine(DSN)

drop_tables(engine)

create_tables(engine)

Session = sessionmaker(bind=engine)

session = Session()

# Функция для добавления информации о пользователе в БД
def add_user(user_data):
    if user_data:
        user = session.query(User).filter_by(id=user_data['id']).scalar()
        if not user:
            user = User(id=user_data['id'])
        session.add(user)
        session.commit()
        return

# Функция для добавления истории поиска пользователя в БД
def add_users(users_data, user_id):
    try:
        for user in users_data:
            users = session.query(User_search_data).filter_by(id=user['id']).scalar()
            if not users:
                users = User_search_data(vk_id=user['id'])
            session.add(users)
            session.commit()
        return
    except (IntegrityError, InvalidRequestError, PendingRollbackError, TypeError):
        session.rollback()
        write_msg(user_id, 'Ошибка', None)
        return False

# Функция для получения истории поиска из БД
def check_users():
    user_search = session.query(User_search_data).order_by(User_search_data.vk_id).all()
    all_users = []
    if user_search:
        for item in user_search:
            all_users.append([item.vk_id])
        return all_users

# Функция для добаления пользователя в избранное в БД
def add_favorite(user):
    found_user = White_list(id=user['id'], first_name=user['first_name'], last_name=user['last_name'],
                                            vk_link=f"https://vk.com/id{user['id']}"
                                            )
    session.add(found_user)
    return session.commit()

# Функция для просмотра списка избранного в БД
def show_favorites():
    db_favorites = session.query(White_list).order_by(White_list.user_id).all()
    favorite_users = []
    if db_favorites:
        for favorite in db_favorites:
            user_info = favorite.first_name + ' ' + favorite.last_name
            vk_link = favorite.vk_link
            favorite_users.append(f"{user_info}\nПрофиль: {vk_link}")
        return '\n'.join(favorite_users)
    return "Список избранных пар пуст."