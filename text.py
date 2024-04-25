import pandas as pd

excel_data = pd.read_excel('information.xlsx')
data = pd.DataFrame(excel_data, columns=['Name', 'Address', 'Contacts', 'Discount', 'Condition', 'Category'])

categories_dict = pd.DataFrame(excel_data, columns=['Название', 'Номер'])
categories = categories_dict['Название'].tolist()
nums = categories_dict['Номер'].tolist()
categories_dict = dict(zip(categories, nums))

START = {
    "greet": "Здравствуйте! Спасибо за пользование картой Гостя.",
    "info": "Для продолжения необходимо согласиться с условиями пользования.\nПосмотреть документы можно по ссылке ()",
}

MAIN = {
    "info": "Добро пожаловать в Калининградскую область. Проведите время, испытав самые положительные эмоции и море впечатлений!",
    "buttons": categories
}


def message(category: str):
    filtered_rows = data[data[""] == 'value']

    OPTION = {
        "info": 0
    }