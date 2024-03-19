import os
import shutil


def create_directories(base_path, num_directories=1):
    for i in range(1, num_directories + 1):
        path = os.path.join(base_path, f"tg_{i}")
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Директория '{path}' успешно создана")
        except OSError as error:
            print(f"Ошибка при создании директории '{path}': {error}")


def copy_files_and_rename(destination_folder, modules_dir, exe_file):
    for folder in os.listdir(destination_folder):
        if folder.startswith("tg_"):
            # Копирование директории modules
            src_modules_path = modules_dir
            dst_modules_path = os.path.join(destination_folder, folder, 'modules')
            shutil.copytree(src_modules_path, dst_modules_path)

            # Копирование и переименование файла Telegram.exe
            file_number = folder.split("_")[1]  # Получаем номер из названия папки (например, tg_1)
            src_exe_path = exe_file
            dst_exe_path = os.path.join(destination_folder, folder, f"Telegram{file_number}.exe")
            shutil.copy(src_exe_path, dst_exe_path)

            print(f"Директория 'modules' и файл 'Telegram{file_number}.exe' скопированы в '{os.path.join(destination_folder, folder)}'")


def main():
    destination_folder = 'C:/tg_ferma/Sorted_farm1'  # Путь к будущей ферме
    modules_dir = 'C:/tg_ferma/tportable-x64.4.15.2/Telegram/modules'  # Путь к директории modules, которую нужно скопировать
    exe_file = 'C:/tg_ferma/tportable-x64.4.15.2/Telegram/Telegram.exe'  # Путь к файлу Telegram.exe, который нужно скопировать и переименовать
    count_tg = 130 # Количество аккаунтов

    create_directories(destination_folder, count_tg)
    copy_files_and_rename(destination_folder, modules_dir, exe_file)


if __name__ == '__main__':
    main()
