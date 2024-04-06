import re

def extract_style(data):
    # Используем списковые включения для извлечения кортежей с ключом 'style'
    styles = [item for item in data if item[0] == 'style']

    # Если есть элементы с ключом 'style', извлекаем первый
    if styles:
        style_tuple = styles[0]
        # Доступ к значению 'style'
        style_value = style_tuple[3]
        return style_value
    else:
        return None

def get_style_level(style_name: str):
    """
    :param style_name: name of the style
    :returns: level if style name begins with heading else None
    """
    if style_name is None:
        return None
    if re.match(r'heading \d', style_name):
        return int(style_name[len("heading "):]) - 1
    return None