import datetime
from colorama import init, Fore, Style
from multiprocessing import Pool, Lock


init()
lock = Lock()


def _getTimeLabel():
    return '[{0:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())


def normal(*args, **kwargs):
    lock.acquire()
    try:
        print(Style.RESET_ALL + _getTimeLabel() + ' ', end='')
        print(*args, **kwargs)
    finally:
        lock.release()


def error(*args, **kwargs):
    lock.acquire()
    try:
        print(Fore.RED + _getTimeLabel(), end='')
        print(" ERROR: ", end='')
        print(*args, **kwargs)
    finally:
        lock.release()


def success(*args, **kwargs):
    lock.acquire()
    try:
        print(Fore.GREEN + _getTimeLabel(), end='')
        print(' SUCCESS: ', end='')
        print(*args, **kwargs)
    finally:
        lock.release()


def warning(*args, **kwargs):
    lock.acquire()
    try:
        print(Fore.YELLOW + _getTimeLabel(), end='')
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
