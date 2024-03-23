import concurrent.futures
from app.src.execution import add_all


num_threads_mtgdecks = 6
num_threads_aetherhub = 4
num_pages_mtgdecks = 1900
num_pages_aetherhub = 180


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads_mtgdecks) as executor:
        for i in range(num_pages_mtgdecks):
            if i % num_threads_mtgdecks == 0:
                executor.submit(add_all, True, i)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads_aetherhub) as executor:
        for i in range(num_pages_aetherhub):
            if i % num_threads_aetherhub == 0:
                executor.submit(add_all, False, i)


if __name__ == "__main__":
    main()
