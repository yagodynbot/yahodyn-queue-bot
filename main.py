from urllib.request import Request, urlopen

from html.parser import HTMLParser

PAGES = {

    "Основная очередь": "https://echerha.gov.ua/workload/truck/checkpoints/1/1/30",

    "Товары УКТ ЗЕД 1-24": "https://echerha.gov.ua/workload/truck/checkpoints/2/1/30",

    "Пустые грузовики": "https://echerha.gov.ua/workload/truck/checkpoints/29/1/30",

}

class PageProbe(HTMLParser):

    def __init__(self):

        super().__init__()

        self.rows = 0

        self.title = False

        self.in_title = False

    def handle_starttag(self, tag, attrs):

        if tag == "tr":

            self.rows += 1

        if tag == "title":

            self.in_title = True

    def handle_endtag(self, tag):

        if tag == "title":

            self.in_title = False

    def handle_data(self, data):

        if self.in_title and data.strip():

            self.title = data.strip()

def check_page(name, url):

    print("\n---", name, "---")

    try:

        request = Request(

            url,

            headers={"User-Agent": "Mozilla/5.0"}

        )

        with urlopen(request, timeout=20) as response:

            html = response.read().decode("utf-8", errors="replace")

            parser = PageProbe()

            parser.feed(html)

            print("HTTP status:", response.status)

            print("Page title:", parser.title)

            print("HTML size:", len(html), "bytes")

            print("Table rows:", parser.rows)

            if parser.rows:

                print("Table data detected")

            else:

                print("No HTML table detected; JS may load data")

    except Exception as error:

        print("Connection error:", str(error))

if __name__ == "__main__":

    print("YAHODYN BOT - CONNECTION TEST")

    for name, url in PAGES.items():

        check_page(name, url)

    print("\nTEST FINISHED")
