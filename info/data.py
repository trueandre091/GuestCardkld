import gspread
from oauth2client.service_account import ServiceAccountCredentials
from random import shuffle

from info.filters import category_f


def connection():
    # Подсоединение к Google Таблице
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("info\\credentials.json", scope)
    client = gspread.authorize(credentials)

    sheet = client.open("information").sheet1
    return sheet


def categories_dict():
    categories = [i[0] for i in connection().batch_get(['H2:H100'])[0]]
    nums = [i[0] for i in connection().batch_get(['I2:I100'])[0]]
    return dict(zip(categories, nums))


def data():
    return connection().batch_get(['A2:G100'])[0]


START = {
    "greet": "Здравствуйте! Спасибо за пользование картой Гостя.",
    "info": "Для продолжения необходимо согласиться с условиями пользования.\n\n<i>Посмотреть документы можно по ссылке <u>https://drive.google.com/file/d/1LsBEuGV9YM_2xvvLXH-0rbh_9BeYU69B/view?usp=sharing</u></i>",
    "photo": "https://i.postimg.cc/d3DJ5c9Q/photo-2024-04-26-09-49-02.jpg"
}

WELCOME = {
    "info": "<b>Добро пожаловать в Калининградскую область. Проведите время, испытав самые положительные эмоции и море впечатлений!</b>",
    "buttons": ["Общая информация", "Поиск по категориям"],
    "photo": "https://i.postimg.cc/B6ZxGPK0/2.png"
}
MENU = {
    "info": "Ниже вы можете выбрать категорию заведений, которые вы бы хотели посетить в нашем регионе!\n\nВы сможете узнать подробную информацию о каждом месте и получить скидку по карте Гостя!",
    "buttons": categories_dict().keys(),
}

OPTION = {
    "buttons": ["Назад", "В избранное", "Вперёд"]
}


class Option:
    def __init__(self, from_user, category) -> None:
        self.from_user = from_user
        self.category = category
        self.rows = category_f(data(), categories_dict(), self.category)
        self.current = []
        self.skipped = []
        self.list_of_rows.append(self)

    list_of_rows = []

    def create_message(self, reverse=False):
        if reverse:
            self.current = self.skipped[-2]
            self.rows.append(self.skipped[-1])
            self.skipped.remove(self.current)
        else:
            shuffle(self.rows)
            self.current = self.rows[0]
            self.rows.remove(self.current)
            self.skipped.append(self.current)

        row = self.current
        text = (f"<b>{row[0]}</b>\n\n"
                f"Адрес: {row[1]}\n"
                f"Ваша скидка: <b>{row[3]}</b> {row[4]}\n\n"
                f"Контакты: {row[2]}")

        return text
