import pandas as pd

excel_data = pd.read_excel('info\\information.xlsx')
data = pd.DataFrame(excel_data, columns=['Name', 'Address', 'Contacts', 'Discount', 'Condition', 'Category'])

categories_dict = pd.DataFrame(excel_data, columns=['Название', 'Номер'])
categories_dict = categories_dict[categories_dict['Название'].notna()]
categories = categories_dict['Название'].tolist()
nums = categories_dict['Номер'].tolist()
categories_dict = dict(zip(categories, nums))


START = {
    "greet": "Здравствуйте! Спасибо за пользование картой Гостя.",
    "info": "Для продолжения необходимо согласиться с условиями пользования.\nПосмотреть документы можно по ссылке ()",\
    "photo": "https://i.postimg.cc/B6ZxGPK0/2.png"
}

MAIN = {
    "info": "Добро пожаловать в Калининградскую область. Проведите время, испытав самые положительные эмоции и море впечатлений!",
    "buttons": categories,
    "photo": "https://i.postimg.cc/597mbggk/3.png"
}


def message(category: str):
    category_value = categories_dict[category]
    if isinstance(category_value, str):
        filtered_rows = data[data["Category"].str.contains(category_value)]
    else:
        print(f"Значение для категории '{category}' не является строкой: {category_value}")

    OPTION = {
        "info": {
            "name": 0
        }
    }


message('Культурный досуг')