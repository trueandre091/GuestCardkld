import gspread
from gspread import Worksheet
from oauth2client.service_account import ServiceAccountCredentials
from random import shuffle

from info.filters import category_f


class Data:
    def __init__(self):
        self.sheet = connection()
        self.categories_dict = categories_dict(self.sheet)
        self.categories = self.categories_dict.keys()
        self.data = data(self.sheet)

    def refresh(self):
        self.sheet = connection()
        self.categories_dict = categories_dict(self.sheet)
        self.data = data(self.sheet)


class Option:
    def __init__(self, DATA: Data, from_user, category) -> None:
        self.from_user = from_user
        self.category = category
        self.rows = category_f(DATA.data, DATA.categories_dict, self.category)
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
        photo = row[6]
        return [text, photo]


def connection():
    # Подсоединение к Google Таблице
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("info\\credentials.json", scope)
    client = gspread.authorize(credentials)

    sheet = client.open("information").sheet1
    return sheet


def categories_dict(sheet: Worksheet):
    categories = [i[0] for i in sheet.batch_get(['H2:H100'])[0]]
    nums = [i[0] for i in sheet.batch_get(['I2:I100'])[0]]
    return dict(zip(categories, nums))


def data(sheet: Worksheet):
    return sheet.batch_get(['A2:G100'])[0]


DATA = Data()
