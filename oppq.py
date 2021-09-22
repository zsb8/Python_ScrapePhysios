from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_futures.sessions import FuturesSession
import requests
import json

from bs4 import BeautifulSoup

with open("physios_updated.json", "r") as f:
    physios = json.load(f)
count = 0
for i in range(10):
    print(f"round{i}")
    with FuturesSession() as session:
        futures = [
            session.get(
                f"https://oppq.qc.ca/en/find-a-professional/results/page/{page_n}/#results"
            )
            for page_n in range(1, 717)
        ]
        # print(json.dumps(physios[name], indent=4))
        for future in as_completed(futures):
            count += 1
            # print(f"Scraping page {count}")
            resp = future.result()
            soup = BeautifulSoup(resp.content, "html.parser")
            for address_el in soup.find_all("address"):
                address_soup = BeautifulSoup(address_el["data-content"], "html.parser")

                name = address_soup.find("p", class_="info-window__name").get_text()

                title = address_soup.find("p", class_="info-window__title").get_text()
                organization = address_soup.find(
                    "p", class_="info-window__organization"
                ).get_text()
                workplace = address_soup.find(
                    "p", class_="info-window__workplace"
                ).get_text()
                coords = address_soup.find("p", class_="info-window__coords").get_text()
                profile = address_soup.find(
                    "p", class_="info-window__profile"
                ).get_text()

                lat = address_el["data-latitude"]
                lon = address_el["data-longitude"]

                if name in physios:
                    # physio already in db
                    continue

                else:
                    print(name)
                    physios[name] = {
                        "title": title,
                        "organizations": [
                            {
                                "name": organization,
                                "workplace": workplace,
                                "coords": coords,
                                "profile": profile,
                                "lat": lat,
                                "lon": lon,
                            }
                        ],
                    }

with open("physios_updated.json", "w", encoding="utf-8") as f:
    json.dump(physios, f, indent=4)
