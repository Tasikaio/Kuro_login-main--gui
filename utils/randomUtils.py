import random

def random_string(alphabet:str, length:int) -> str:
    random_string_list = [random.choice(alphabet) for i in range(length)]
    return "".join(random_string_list)
