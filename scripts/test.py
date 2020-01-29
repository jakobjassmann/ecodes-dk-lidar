import multiprocessing
import re

def f(x):
    current = multiprocessing.current_process()


    return re.sub('[(),]', '', str(current._identity))


if __name__ == '__main__':

    p = multiprocessing.Pool(processes=54)
    print p.map(f, range(100))