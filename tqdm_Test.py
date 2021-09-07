# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-31 17:50

from time import sleep
import random
from tqdm import tqdm
import asyncio

L = list(range(24))  # works until 23, breaks starting at 24


def progresser(n):
    text = f'#{n}'

    sampling_counts = 10
    with tqdm(total=sampling_counts, desc=text, position=n + 1) as pbar:
        for i in range(sampling_counts):
            sleep(random.uniform(0, 1))
            pbar.update(1)


def test01(n):
    text = f'#{n}'

    sampling_counts = 10
    with tqdm(total=sampling_counts, desc=text, position=n + 1) as pbar:
        for i in range(sampling_counts):
            sleep(random.uniform(0, 1))
            pbar.update(1)


async def test02(n):
    text = f'#{n}'

    sampling_counts = 10
    with tqdm(total=sampling_counts, desc=text, position=n + 1) as pbar:
        for i in range(sampling_counts):
            sleep(random.uniform(0, 1))
            pbar.update(1)

async def main():
    pass

if __name__ == '__main__':
    pass
    # freeze_support()
    # p = Pool(processes=None, initargs=(RLock(),), initializer=tqdm.set_lock)
    # p.map(progresser, L)
    # print('\n' * (len(L) + 1))

    # asyncio.run(main())
