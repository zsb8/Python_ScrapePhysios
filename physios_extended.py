from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_futures.sessions import FuturesSession
import requests
import json

from bs4 import BeautifulSoup


with open("physios_updated.json", "r") as f:
    physios = json.load(f)


count = 0

for page_n in range(1, 717):
    print("Scrapping page {}".format(page_n))
    URL = "https://oppq.qc.ca/en/find-a-professional/results/page/{}/#results".format(
        page_n
    )
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    physio_links = []
    for result_item in soup.find_all("li", class_="results__item"):
        physio_links.append(result_item.find("a", class_="link-button")["href"])

    with FuturesSession() as session:
        futures = [session.get("https://oppq.qc.ca" + link) for link in physio_links]
        # print(json.dumps(physios[name], indent=4))
        for future in as_completed(futures):
            resp = future.result()
            count += 1
            try:

                soup = BeautifulSoup(resp.content, "html.parser")

                name = (
                    soup.find("h1", class_="page-header__title")
                    .get_text()
                    .split(",")[0]
                )
                print(f"physio {count}: {name}")
                if not (name in physios):
                    print(f"Physio not found: {name}")
                    physios[name] = dict()
                    continue

                clientele_groups = soup.find(
                    "div", class_="clientele row align-items-end"
                ).find_all("span")

                physios[name]["clientele groups"] = [
                    group.get_text() for group in clientele_groups
                ]

                lists = soup.find_all("ul", class_="professional__list")
                physios[name]["languages"] = lists[0].find("li").get_text().split(", ")
                physios[name]["approaches"] = [
                    el.get_text() for el in lists[1].find_all("li")
                ]
                physios[name]["reasons"] = [
                    el.get_text() for el in lists[2].find_all("li")
                ]
            except TypeError as e:
                print(e)
                print(name)
                continue
            except IndexError:
                print("Incomplete profile")
                print(name)
                print(physios[name])
                continue

with open("physios_extended.json", "w", encoding="utf-8") as f:
    json.dump(physios, f, indent=4)
