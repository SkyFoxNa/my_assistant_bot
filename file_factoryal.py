"""
Напишіть реалізацію функції factorize, яка приймає список чисел та повертає список чисел,
на які числа з вхідного списку поділяються без залишку.
Реалізуйте синхронну версію та виміряйте час виконання.
Потім покращіть продуктивність вашої функції, реалізувавши використання кількох ядер
процесора для паралельних обчислень і замірьте час виконання знову. Для визначення кількості
ядер на машині використовуйте функцію cpu_count() з пакета multiprocessing
Для перевірки правильності роботи алгоритму самої функції можете скористатися тестом:
"""
from time import time
from multiprocessing import Pool, current_process, cpu_count
import logging
import concurrent.futures

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def factorize(numbers: list) :
    result = []
    for i in numbers :
        lst = []
        for num in range(1, i + 1) :
            if i % num == 0 :
                lst.append(num)
        result.append(lst)
    # print(result)
    return result


def multifacrorize(number: int) :
    lst = []
    for num in range(1, number + 1) :
        if number % num == 0 :
            lst.append(num)
    return lst


if __name__ == '__main__' :
    input_data = [128, 255, 99999, 10651060, 123142342, 345345345]
    start = time()
    a, b, c, d, *_ = factorize(input_data)
    end = time()
    print(f'Single proc: {end - start}')
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106,
                 1521580, 2130212, 2662765, 5325530, 10651060]

    # core_counts = cpu_count()
    core_counts = 2
    print(core_counts)
    start = time()
    with Pool(processes = core_counts) as pool :
        logger.debug(pool.map(multifacrorize, input_data))
    end = time()
    print(f'Multiproc proc: {end - start}')

    start = time()
    with concurrent.futures.ProcessPoolExecutor(core_counts) as executor :
        executor.map(multifacrorize, input_data)
    end = time()
    print(f'Multiproc concurrent: {end - start}')
