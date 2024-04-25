import pandas as pd

excel_data = pd.read_excel('information.xlsx')
data = pd.DataFrame(excel_data, columns=['Name', 'Address', 'Contacts', 'Discount', 'Condition', 'Category'])
print(data)

START = {
    "greet": "Здравствуйте! Спасибо за пользование 'Картой Гостя'.",
    "info": "Для продолжения необходимо согласиться с условиями пользования.\nПосмотреть документы можно по ссылке ()",
}

MAIN = {
    "info": "Добро пожаловать в Калининградскую область. Проведите время, испытав самые положительные эмоции и море впечатлений!",
    "buttons": {

    }
}