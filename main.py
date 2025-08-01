from parsers.link_parser import *
from multiprocessing import Process

parsers = {
    "1": parser_labirint_doors,
    "https://labirintdoors.ru/": parser_labirint_doors,
    "2": parser_bunker_doors,
    "https://bunkerdoors.ru/": parser_bunker_doors,
    "3": parser_intercon,
    "https://intecron-msk.ru/": parser_intercon,
    "4": parser_asd,
    "https://as-doors.ru/": parser_asd,
    "5": parser_ratibor,
    "https://dveri-ratibor.ru/": parser_ratibor,
    "6": parser_termo_door,
    "https://termo-door.ru/": parser_termo_door,
    "7": parser_mxd,
    "https://mxdoors.ru/": parser_mxd,
    "8": parser_fabric_doors,
    "https://xn--80aeahafcjmeq0c7ah.xn--p1ai/": parser_fabric_doors,
    "9": parser_command_doors,
    "https://cmdoors.ru/": parser_command_doors,
    "10": parser_sudar,
    "https://closedoor.ru/": parser_sudar,
    "11": parser_str,
    "https://str12.ru/": parser_str,
    "12": parser_forpost,
    "https://forpostroznica.ru/": parser_forpost,
    "13": parser_007,
    "https://doors007.ru/": parser_007,
}

def print_help():
    print(
        "Вот список сайтов пригодных для парсинга (можно вводить номера или ссылки, разделяя пробелами):\n"
        "1 : https://labirintdoors.ru/\n"
        "2 : https://bunkerdoors.ru/\n"
        "3 : https://intecron-msk.ru/\n"
        "4 : https://as-doors.ru/\n"
        "5 : https://dveri-ratibor.ru/\n"
        "6 : https://termo-door.ru/\n"
        "7 : https://mxdoors.ru/\n"
        "8 : https://xn--80aeahafcjmeq0c7ah.xn--p1ai/\n"
        "9 : https://cmdoors.ru/\n"
        "10 : https://closedoor.ru/\n"
        "11 : https://str12.ru/\n"
        "12 : https://forpostroznica.ru/\n"
        "13 : https://doors007.ru/\n"
        "\nПример: `1 3 5` запустит три парсера параллельно.\n"
        "Чтобы выйти из программы, введите exit"
    )

if __name__ == "__main__":
    while True:
        user_input = input("Введите ссылку(и) сайта или help / -h для подсказки:\n").strip()
        
        if user_input in ("help", "-h"):
            print_help()
            continue
        elif user_input == "exit":
            break

        inputs = user_input.split()
        processes = []

        for entry in inputs:
            parser_func = parsers.get(entry)
            if parser_func:
                p = Process(target=parser_func)
                processes.append(p)
                p.start()
            else:
                print(f"Неизвестный ввод: {entry}")

        for p in processes:
            p.join() 
