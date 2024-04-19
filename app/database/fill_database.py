import concurrent.futures
from app.src.execution import add_all


num_threads = 8
num_pages_mtgdecks = 1900
num_pages_aetherhub = 180


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(1, num_threads + 1):
            executor.submit(add_all_pages, True, i, num_pages_mtgdecks + 1, num_threads)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(1, num_threads + 1):
            executor.submit(add_all_pages, False, i, num_pages_aetherhub + 1, num_threads)


def add_all_pages(mtgdecks, start_page, num_pages, step):
    for i in range(start_page, num_pages, step):
        add_all(mtgdecks=mtgdecks, start_page=i)


if __name__ == "__main__":
    main()
