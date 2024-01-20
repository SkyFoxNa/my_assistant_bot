from pathlib import Path
import shutil
from tqdm import tqdm
import time
from time import sleep, ctime
import re
from threading import Thread, Barrier
import logging

# normalize
# Створюємо змінну з українською абеткою
CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
# Створюємо змінну (список) для транслейту
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "i", "ji", "g")
# Створюємо порожній словник для транслейту
CONVERTS = dict()

# Заповнюємо словник
for cyrillic, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    CONVERTS[ord(cyrillic)] = latin
    CONVERTS[ord(cyrillic.upper())] = latin.upper()


# Створюємо функцію для чищення від усіх зайвих символів і перетворюємо та заміняємо на транслейт
def normalize(name: str) -> str:
    translate_name = re.sub(r'\W', '_', name.translate(CONVERTS))
    return translate_name

# file_parser
# Створюємо порожні списки для зображень


JPEG_IMAGES = []
JPG_IMAGES = []
PNG_IMAGES = []
SVG_IMAGES = []
GIF_IMAGES = []

# Створюємо порожні списки для відео
AVI_VIDEO = []
MP4_VIDEO = []
MOV_VIDEO = []
MKV_VIDEO = []

# Створюємо порожні списки для музики
MP3_AUDIO = []
OGG_AUDIO = []
WAV_AUDIO = []
AMR_AUDIO = []

# Створюємо порожні списки для документів
DOC_DOCUMENTS = []
DOCX_DOCUMENTS = []
TXT_DOCUMENTS = []
PDF_DOCUMENTS = []
XLSX_DOCUMENTS = []
PPTX_DOCUMENTS = []

# Створюємо порожній список для архівів
ARCHIVES = []

# Створюємо порожній список для решти
MY_OTHER = []

# Створюємо словник з розширеннями та відповідними ним списками
REGISTER_EXTENSION = {
    'JPEG': [JPEG_IMAGES, 'images'],
    'JPG': [JPG_IMAGES, 'images'],
    'PNG': [PNG_IMAGES, 'images'],
    'GIF': [GIF_IMAGES, 'images'],
    'SVG': [SVG_IMAGES, 'images'],
    'AVI': [AVI_VIDEO, 'video'],
    'MP4': [MP4_VIDEO, 'video'],
    'MOV': [MOV_VIDEO, 'video'],
    'MKV': [MKV_VIDEO, 'video'],
    'MP3': [MP3_AUDIO, 'audio'],
    'OGG': [OGG_AUDIO, 'audio'],
    'WAW': [WAV_AUDIO, 'audio'],
    'AMR': [AMR_AUDIO, 'audio'],
    'DOC': [DOC_DOCUMENTS, 'documents'],
    'DOCX': [DOCX_DOCUMENTS, 'documents'],
    'TXT': [TXT_DOCUMENTS, 'documents'],
    'PDF': [PDF_DOCUMENTS, 'documents'],
    'XLSX': [XLSX_DOCUMENTS, 'documents'],
    'PPTX': [PPTX_DOCUMENTS, 'documents'],
    'ZIP': [ARCHIVES, 'archives'],
    'GZ': [ARCHIVES, 'archives'],
    'TAR': [ARCHIVES, 'archives'],
}

# Створюємо порожній список для шляху до папок
FOLDERS = []
# Створюємо порожню множину для розширень
EXTENSIONS = set()
# Створюємо порожню множину для невідомих
UNKNOWN = set()


# Відокремлюємо суфікс і перетворюємо на великі літери
def get_extension(name: str) -> str:
    return Path(name).suffix[1:].upper()


# Проходимося по папці із сортувальними файлами
def scan(folder: Path):
    for item in folder.iterdir():
        # Робота з папкою
        if item.is_dir():  # перевіряємо чи обєкт папка
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'MY_OTHER'):
                FOLDERS.append(item)
                scan(item)
            continue

        # Робота з файлом
        extension = get_extension(item.name)  # беремо розширення файлу
        full_name = folder / item.name  # беремо повний шлях до файлу
        if not extension:
            MY_OTHER.append(full_name)
        else:
            try:  # перевіряємо з розширень
                register_extension = REGISTER_EXTENSION[extension][0]
                register_extension.append(full_name)
                EXTENSIONS.add(extension)
            except KeyError:
                UNKNOWN.add(extension)
                MY_OTHER.append(full_name)


# Проводимо очищення і створюємо директорію, а не директорію з розширенням для папок і файлів.
def handle_media(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    name_normalize = normalize(file_name.stem) + file_name.suffix
    file_name.replace(target_folder / name_normalize)


# Проводимо очищення та створюємо директорію, розпаковуємо архів для архівів.
def handle_archive(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(file_name.name.replace(file_name.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(file_name.absolute()), str(folder_for_file.absolute()))
    except shutil.ReadError:
        folder_for_file.rmdir()
        return
    file_name.unlink()


def process_files(file_list, target_folder, file_type):
    for file in tqdm(file_list, desc=f'\033[38;2;10;235;190mProcessing {file_type}',
                     unit=" file\033[0m", ncols=100):
        handle_media(file, target_folder)
        time.sleep(0.05)


def process_archives(archive_list, target_folder):
    for file in tqdm(archive_list, desc='\033[38;2;10;235;190mProcessing of archives',
                     unit=" file\033[0m", ncols=100):
        handle_archive(file, target_folder)
        time.sleep(0.05)


def process_folders(folder_list):
    for folder in tqdm(folder_list[::-1], desc='\033[38;2;10;235;190mDeleting empty folders',
                       unit=" folder\033[0m", ncols=100):
        time.sleep(0.05)
        try:
            folder.rmdir()
        except OSError:
            print(f'\033[91mError during remove folder {folder}\033[0m')


# Основний модуль логіки
def main(folder: Path):
    logging.basicConfig(level = logging.DEBUG, format = '%(threadName)s %(message)s')
    logging.debug(f'Start program {ctime()}')
    scan(folder)

    threads = []
    for key, value in REGISTER_EXTENSION.items():
        if value[1] not in ['archives']:

            logging.debug(f'Start sorter {key} {ctime()}')
            thread = Thread(target = process_files, args = (value[0], folder / value[1] / key, key,))
            thread.start()
            threads.append(thread)
            # process_files(value[0], folder / value[1] / key, key)

    [el.join() for el in threads]
    logging.debug(f'Start sorter archives {ctime()}')
    process_archives(ARCHIVES, folder / 'archives')

    # Проходимо за всіма знайденими списками для MY_OTHER
    count_star = 0
    for file in tqdm(MY_OTHER, desc = '\033[38;2;10;235;190mProcessing other files',
                     unit = " file\033[0m", ncols = 100):
        handle_media(file, folder / 'MY_OTHER')
        count_star += 1
        time.sleep(0.05)

    count_star = 0
    for folder in tqdm(FOLDERS[::-1], desc = '\033[38;2;10;235;190mDeleting empty folders',
                     unit = " file\033[0m", ncols = 100):
        count_star += 1
        time.sleep(0.05)
        # Видаляємо пусті папки після сортування
        try:
            folder.rmdir()
        except OSError:
            print(f'\033[91mError during remove folder {folder}\033[0m')


def sorteds_menu():
    print(f'\033[38;2;10;235;190mCopy the files to be sorted into a folder'
          f' \033[91mtrash_folder'
          f'\033[38;2;10;235;190m in this project and press Enter to sort them.\033[0m')
    user_input = input('\033[38;2;10;235;190mPress Enter to sort them.\033[0m')
    folder_process = Path('trash_folder')
    main(folder_process.resolve())


if __name__ == "__main__":
    # items = list(range(100))
    # for item in tqdm(items, desc='\033[38;2;10;235;190mПрогресс', unit='элемент\033[0m', ncols=100):
    #     # Симулируем задержку для наглядности
    #     time.sleep(0.05)
    # folder_process = Path(sys.argv[1])
    folder_process = Path('trash_folder')
    main(folder_process.resolve())
