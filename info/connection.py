import gspread
from gspread import Worksheet
from oauth2client.service_account import ServiceAccountCredentials


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
        self.rows = category_filter(DATA.data, DATA.categories_dict, self.category)
        self.index = -1
        self.list_of_rows.append(self)

    list_of_rows = []

    def create_message(self, action=0):
        if action == 1:
            self.index -= 1
            if self.index < 0:
                self.index = 0
        elif action == 0:
            self.index += 1

        flag1 = False if self.index == (len(self.rows) - 1) else True
        flag0 = False if self.index == 0 else True

        row = self.rows[self.index]
        text = (f"<b>{row[0]}</b>\n\n"
                f"Адрес: {row[1]}\n"
                f"Ваша скидка: <b>{row[3]}</b> {row[4]}\n\n"
                f"Контакты: {row[2]}")
        photo = row[6]
        return [text, photo, flag0, flag1]


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


def category_filter(data: list, categories_dict: dict, category: str):
    num = categories_dict[category]
    return [row for row in data if num in row[5].split()]


DATA = Data()
