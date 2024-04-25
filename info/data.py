import gspread
from oauth2client.service_account import ServiceAccountCredentials
from random import shuffle

from info.filters import category_f

# Подсоединение к Google Таблице
scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("info\\credentials.json", scope)
client = gspread.authorize(credentials)

sheet = client.open("information").sheet1
data = sheet.batch_get(['A2:G100'])[0]
categories = [i[0] for i in sheet.batch_get(['H2:H100'])[0]]
nums = [i[0] for i in sheet.batch_get(['I2:I100'])[0]]
categories_dict = dict(zip(categories, nums))

START = {
    "greet": "Здравствуйте! Спасибо за пользование картой Гостя.",
    "info": "Для продолжения необходимо согласиться с условиями пользования.\nПосмотреть документы можно по ссылке ()",
    "photo": "https://i.postimg.cc/B6ZxGPK0/2.png"
}

MAIN = {
    "info": "Добро пожаловать в Калининградскую область. Проведите время, испытав самые положительные эмоции и море впечатлений!",
    "buttons": categories,
    "photo": "https://i.postimg.cc/597mbggk/3.png"
}

OPTION = {
    "buttons": ["Назад", "В избранное", "Вперёд"]
}


class Option:
    def __init__(self, from_user, category) -> None:
        self.from_user = from_user
        self.category = category
        self.rows = category_f(data, categories_dict, self.category)
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
        text = (f"*{row[0]}*\n\n"
                f"Адрес: {row[1]}\n"
                f"Ваша скидка: *{row[3]}* {row[4]}\n"
                f"Контакты: {row[2]}")

        return text

