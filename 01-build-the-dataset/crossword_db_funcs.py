"""Module containing functions for building and working with the crossword database."""

import sqlite3
import os


import sqlite3

def create_crossword_db(dbpath: str = "crossword.db") -> None:
    """Create the crossword database with the required tables."""
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()

    # Create crossword_url table
    c.execute(
        """CREATE TABLE crossword_url (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            processed BOOLEAN,
            date DATE UNIQUE
        );"""
    )

    # Create questions table
    c.execute(
        """CREATE TABLE questions (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT UNIQUE
        );"""
    )

    # Create answers table
    c.execute(
        """CREATE TABLE answers (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            answer TEXT
        );"""
    )

    # Create questions_date table
    c.execute(
        """CREATE TABLE questions_date (
            question_key INTEGER,
            date_key INTEGER,
            FOREIGN KEY(question_key) REFERENCES questions(pk),
            FOREIGN KEY(date_key) REFERENCES crossword_url(pk)
        );"""
    )

    # Create answers_date table
    c.execute(
        """CREATE TABLE answers_date (
            answer_key INTEGER,
            date_key INTEGER,
            FOREIGN KEY(answer_key) REFERENCES answers(pk),
            FOREIGN KEY(date_key) REFERENCES crossword_url(pk)
        );"""
    )

    # Create question_answer table
    c.execute(
        """CREATE TABLE question_answer (
            question_key INTEGER,
            answer_key INTEGER,
            FOREIGN KEY(question_key) REFERENCES questions(pk),
            FOREIGN KEY(answer_key) REFERENCES answers(pk)
        );"""
    )
    # Create sitemap_url table
    c.execute(
        """CREATE TABLE sitemap_url (
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            sitemap_url TEXT UNIQUE,
            processed BOOLEAN
        );"""
    )

    conn.commit()
    conn.close()


def fetch_or_build_crossword_db(dbpath: str = "crossword.db", rebuild: bool = False) -> sqlite3.Connection:
    """
    Get the connection to the crossword database, creating it if it doesn't exist.

    rebuild - if True, rebuild the database even if it exists
    """
    if rebuild or not os.path.exists(dbpath):
        # try to delete the database file if it exists
        try:
            os.remove(dbpath)
        except FileNotFoundError:
            pass
        create_crossword_db(dbpath)
    return sqlite3.connect(dbpath)


def insert_crossword_url(conn: sqlite3.Connection, url: str, processed: bool, date: str) -> None:
    """Insert a URL into the crossword_url table."""
    c = conn.cursor()
    c.execute(
        """INSERT INTO crossword_url (url, processed, date)
        VALUES (?, ?, ?);""",
        (url, processed, date)
    )
    conn.commit()


def insert_sitemap_url(conn: sqlite3.Connection, url: str, processed: bool) -> None:
    """Insert a URL into the sitemap_url table."""
    c = conn.cursor()
    try:
        c.execute(
        """INSERT INTO sitemap_url (sitemap_url, processed)
        VALUES (?, ?);""",
        (url, processed)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        # print(f"IntegrityError: {e}")
        conn.rollback()

def get_unprocessed_sitemap_urls(conn: sqlite3.Connection) -> list:
    c = conn.cursor()
    c.execute(
        """SELECT * FROM sitemap_url WHERE processed = 0;"""
    )
    return c.fetchall()

def mark_sitemap_url_processed(conn: sqlite3.Connection, pk: int) -> None:
    c = conn.cursor()
    c.execute(
        """UPDATE sitemap_url
        SET processed = 1
        WHERE pk = ?;""",
        (pk,)
    )
    conn.commit()

def get_crossword_urls(conn: sqlite3.Connection) -> list:
    c = conn.cursor()
    c.execute(
        """SELECT * FROM crossword_url;"""
    )
    return c.fetchall()

def get_unprocessed_crossword_urls(conn: sqlite3.Connection) -> list:
    c = conn.cursor()
    c.execute(
        """SELECT * FROM crossword_url WHERE processed == 0;"""
    )
    return c.fetchall()


def log_clue_and_answer(conn, clue: str, answer: str, date_key: int) -> None:
    c = conn.cursor()

    # if a clue is not found in the questions table, insert it and save the pk with a question_pk variable
    c.execute(
        """INSERT OR IGNORE INTO questions (question) VALUES (?);""",
        (clue,)
    )
    c.execute(
        """SELECT pk FROM questions WHERE question = ?;""",
        (clue,)
    )
    question_pk = c.fetchone()[0]

    # if an answer is not found in the answers table, insert it and save the pk with an answer_pk variable
    c.execute(
        """INSERT OR IGNORE INTO answers (answer) VALUES (?);""",
        (answer,)
    )
    c.execute(
        """SELECT pk FROM answers WHERE answer = ?;""",
        (answer,)
    )
    answer_pk = c.fetchone()[0]
    # insert the question_pk and date_key into the questions_date table
    c.execute(
        """INSERT INTO questions_date (question_key, date_key) VALUES (?, ?);""",
        (question_pk, date_key)
    )
    # insert the answer_pk and date_key into the answers_date table
    c.execute(
        """INSERT INTO answers_date (answer_key, date_key) VALUES (?, ?);""",
        (answer_pk, date_key)
    )

    # insert the question_pk and answer_pk into the question_answer table
    c.execute(
        """INSERT OR IGNORE INTO question_answer (question_key, answer_key) VALUES (?, ?);""",
        (question_pk, answer_pk)
    )


def mark_crossword_url_processed(conn: sqlite3.Connection, pk: int) -> None:
    c = conn.cursor()
    c.execute(
        """UPDATE crossword_url
        SET processed = 1
        WHERE pk = ?;""",
        (pk,)
    )
    conn.commit()