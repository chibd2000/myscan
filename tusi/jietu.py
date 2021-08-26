from playwright.async_api import async_playwright
import asyncio
from urllib.parse import urlparse


def filename():
    with open('uu.txt', 'r', encoding='utf-8') as fp:
        wordlist = fp.read().splitlines()
        htmls = set(
            url.strip() if url.strip().startswith(('http://', 'https://')) else ''.join(('http://', url.strip())) for
            url in wordlist if len(url) > 1)
    return htmls


async def get(context, sem, url):
    async with sem:
        page_two = await context.new_page()
        try:
            await  page_two.goto(url)
            name = await page_two.title()
            await  page_two.screenshot(path=f'png/{urlparse(url).netloc}_{name}.png', )
            print(f'截图成功当前名称{urlparse(url).netloc}_{name}.png')
        except  Exception as e:
            pass
            # print(e)
        await page_two.close()


async def main():
    urls = filename()
    async with async_playwright() as asp:
        browse = await  asp.chromium.launch()
        context = await browse.new_context()
        sem = asyncio.Semaphore(10)
        tasks = [asyncio.ensure_future(get(context, sem, url)) for url in urls]
        # 实现异步嵌套
        dones, pendings = await asyncio.wait(tasks)
        for t in dones:
            t.result()
        # 关闭浏览器


if __name__ == '__main__':
    asyncio.run(main())
