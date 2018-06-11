import datetime
from colorama import init, Fore, Style
from multiprocessing import Pool, Lock


init()
lock = Lock()


def normal(*args, **kwargs):
    lock.acquire()
    try:
        print(Style.RESET_ALL + '[{0:%Y-%m-%d %H:%M:%S}] '.format(datetime.datetime.now()), end='')
        print(*args, **kwargs)
    finally:
        lock.release()


def error(*args, **kwargs):
    lock.acquire()
    try:
        print(Fore.RED + '[{0:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now()), end='')
        print(" ERROR: ", end='')
        print(*args, **kwargs)
    finally:
        lock.release()


def success(*args, **kwargs):
    lock.acquire()
    try:
        print(Fore.GREEN + '[{0:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now()), end='')
        print(' SUCCESS: ', end='')
        print(*args, **kwargs)
    finally:
        lock.release()


def warning(*args, **kwargs):
    lock.acquire()
    try:
        print(Fore.YELLOW + '[{0:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now()), end='')
        print(' WARNING: ', end='')
        print(*args, **kwargs)
    finally:
        lock.release()


if __name__ == '__main__':
    def f(x):
        normal("This is normal text")
        error("This is error text")
        success("This is success text")

    with Pool(processes=4) as pool:
        pool.map(f, range(4))
