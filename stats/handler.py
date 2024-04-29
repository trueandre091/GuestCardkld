import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from DB.database import get_statistics, get_active_users
from info.connection import DATA

TITLES = ["start", "category", "like", "dislike", "cancel"]
PERIODS = {
    "День": timedelta(days=1),
    "Неделя": timedelta(weeks=1),
    "Месяц": timedelta(days=31),
    "Квартал": timedelta(days=91),
    "Год": timedelta(days=365)
}


def plot_statistics(start_date, end_date, path='stats\\graphics'):
    data = get_statistics(start_date, end_date)
    active_users = get_active_users(start_date, end_date)

    events = [item[0] for item in data]
    timestamps = [datetime.strptime(item[2], '%Y-%m-%d %H:%M:%S') for item in data]

    categories_items = [item for item in data if item[0] == TITLES[1]]

    plt.figure(figsize=(15, 10))
    plt.scatter(timestamps, events, marker='o')
    plt.gcf().autofmt_xdate()
    date_format = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.title('Активность бота')
    plt.xlabel('Время')
    plt.ylabel('Событие')
    plt.savefig(f"{path}\\scatter.png")
    plt.close()

    categories_dict = {v: k for k, v in DATA.categories_dict.items()}
    plt.figure(figsize=(15, 10))
    plt.bar([categories_dict[item[1]] for item in categories_items],
            [len([buff[1] for buff in categories_items if buff[1] == item[1]]) for item in categories_items])
    plt.title("Столбчатая диаграмма популярности категорий")
    plt.xlabel("Категории")
    plt.ylabel("Кол-во просмотров")
    plt.savefig(f"{path}\\bar.png")
    plt.close()

    users = [len([buff[1] for buff in active_users if buff[1] == item[1]]) for item in active_users]
    timestamps = [datetime.strptime(item[1].split(".")[0], '%Y-%m-%d %H:%M:%S') for item in active_users]
    plt.figure(figsize=(15, 10))
    plt.bar(timestamps, users, width=0.3)
    plt.gcf().autofmt_xdate()
    date_format = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.title("Количество активных пользователей")
    plt.xlabel("Периоды")
    plt.ylabel("Кол-во пользователей")
    plt.savefig(f"{path}\\bar1.png")
    plt.close()

    return path
