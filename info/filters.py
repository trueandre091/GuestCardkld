def incategory(num: int, row: list):
    return True if num in row[5].split() else False


def category_f(data: list, categories_dict: dict, category: str):
    num = categories_dict[category]
    return [row for row in data if incategory(num, row)]
