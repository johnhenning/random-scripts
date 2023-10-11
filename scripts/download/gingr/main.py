import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from hf_argparser import HfArgumentParser
from dataclasses import dataclass
import bs4
import httpx


@dataclass
class Arguments:
    url: str
    base_path: str = "bagels_photos"


async def main(args: Arguments):
    base_path = Path(args.base_path)
    base_path.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.webkit.launch(slow_mo=50)
        context = await browser.new_context(java_script_enabled=True)
        page = await context.new_page()

        res = await page.goto(args.url)
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        await browser.close()

        soup = bs4.BeautifulSoup(content, features="html.parser")
        div = soup.find(attrs={"class": "css-1dbjc4n r-18u37iz r-16y2uox"})
        assert div
        imgs = div.find_all("img")
        img_urls = [img["src"] for img in imgs]
        print(img_urls)
        date = "-".join(img_urls[0].split("/")[-4:-1])
        date_path = base_path / date
        date_path.mkdir(parents=True, exist_ok=True)

        for url in img_urls:
            res = httpx.get(url)
            body = res.read()
            filename = url.split("/")[-1]
            path = date_path / filename
            path.write_bytes(body)


def parse_args():
    parser = HfArgumentParser((Arguments,))
    args = parser.parse_args_into_dataclasses()[0]
    return args


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
