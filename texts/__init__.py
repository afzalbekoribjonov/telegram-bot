from types import SimpleNamespace
from texts import uz, ru


def get_texts(lang: str):
    return SimpleNamespace(**(uz.text if lang == 'uz' else ru.text))