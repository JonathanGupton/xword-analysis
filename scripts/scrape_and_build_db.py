
import re
import sqlite3

from bs4 import BeautifulSoup
import requests
import tqdm

from crossword_db_funcs import insert_sitemap_url
from crossword_db_funcs import insert_crossword_url
from crossword_db_funcs import fetch_or_build_crossword_db
from crossword_db_funcs import get_unprocessed_sitemap_urls
from crossword_db_funcs import get_unprocessed_crossword_urls
from crossword_db_funcs import mark_sitemap_url_processed
from crossword_db_funcs import mark_crossword_url_processed
from crossword_db_funcs import log_clue_and_answer
from crossword_site_funcs import get_sitemap
from crossword_site_funcs import request_with_exponential_backoff


SITEMAP_PATTERN = r"https://nytcrosswordanswers\.org/post-sitemap\d*\.xml"
CROSSWORD_URL_PATTERN = r"https://nytcrosswordanswers\.org/nyt-crossword-answers-(?P<date>\d\d-\d\d-\d\d)/"


def process_sitemap_post_url(conn: sqlite3.Connection, url: str) -> None:
    r = request_with_exponential_backoff(url)
    bs = BeautifulSoup(r.content, features="xml")
    for tag in bs.find_all('loc'):
        if match_ := re.match(CROSSWORD_URL_PATTERN, tag.text):
            insert_crossword_url(conn, tag.text, False, match_['date'])


if __name__ == '__main__':
    # Build or fetch the database connection
    conn = fetch_or_build_crossword_db(rebuild=False)

    # Crawl the site map for URLs and store in the database
    sitemap_soup = get_sitemap()

    for tag in tqdm.tqdm(sitemap_soup.find_all('loc')):
        if re.match(SITEMAP_PATTERN, tag.text):
            sitemap_post_url = tag.text
            insert_sitemap_url(conn, sitemap_post_url, False)

    for sitemap_url_row in tqdm.tqdm(get_unprocessed_sitemap_urls(conn)):
        pk, sitemap_url, processed = sitemap_url_row
        r = request_with_exponential_backoff(sitemap_url)
        try:
            r.raise_for_status()
            bs = BeautifulSoup(r.content, features="xml")
            for tag in bs.find_all('loc'):
                if re.match(CROSSWORD_URL_PATTERN, tag.text):
                    insert_crossword_url(conn, tag.text, False, re.match(CROSSWORD_URL_PATTERN, tag.text)['date'])
            mark_sitemap_url_processed(conn, pk)
        except requests.HTTPError as e:
            print(f"HTTP error occured: {e}")
            continue
        except Exception as e:
            print(f"An error occured: {e}")
            continue


    # Crawl the crossword URLs and store the clues and answers in the database
    for crossword_url_row in tqdm.tqdm(get_unprocessed_crossword_urls(conn)):
        cw_pk, crossword_url, processed, date = crossword_url_row
        r = request_with_exponential_backoff(crossword_url)
        try:
            r.raise_for_status()
            bs = BeautifulSoup(r.content, features="html.parser")
            nywrap = bs.find('div', class_='nywrap')
            for tag in nywrap.find_all('li'):
                clue = tag.a.text
                answer = tag.span.text
                log_clue_and_answer(conn, clue, answer, cw_pk)
            mark_crossword_url_processed(conn, cw_pk)
        except requests.HTTPError as e:
            print(f"HTTP error occured: {e}")
            continue
        except Exception as e:
            print(f"An error occured: {e}")
            continue

