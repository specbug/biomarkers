import multiprocessing


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1