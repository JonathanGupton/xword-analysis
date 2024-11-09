Create the database and build the tables and relations




Table:  crossword_url 

| pk | url_stub (str) | processed (bool) |date (date)
|---|----------------|------------------|---|
|1|nyt-crossword-answers-01-07-11/|FALSE|2011-01-07|


Go through each URL in the URL table and call the page
Find the question/answer table:

```html
<div class="nywrap">
  <ul>
    <li>
      <a href="...">{INNER VALUE IS THE QUESTION}></a>
      <span>{THIS IS THE ANSWER}</span>
    </li>
  </ul>
</div>
```

There are two unordered lists - One for the horizontal clues/answer and one for the vertical.

There is an h3/span that precedes each \<UL> with the value "nydir ve" and "nydir hz" 

For each question/answer, log these in the various questions and answers table

Table:  questions

| pk | question (str, index)               |
| ---|-------------------------------------|
|1| "THEIR SCORES MAY BE ON TRANSCRIPTS" |

Table:  answers

| pk | answer (str, index) |
| ---|---------------------|
|1| "SATS"              |

Table:  questions-date


| question_key | date_key |
|--------------|----------|
| 1            | 1        |


Table:  answers-date

| answer_key | date_key |
|------------|----------|
| 1          | 1        |


Table:  question-answer

| question_key | answer_key |
|--------------|------------|
| 1            | 1          |



Once complete for the URL, mark this url as processed.


```mermaid
erDiagram
    CROSSWORD_URL ||--o{ QUESTIONS_DATE : "has"
    CROSSWORD_URL ||--o{ ANSWERS_DATE : "has"
    QUESTIONS ||--o{ QUESTIONS_DATE : "has"
    ANSWERS ||--o{ ANSWERS_DATE : "has"
    QUESTIONS ||--o{ QUESTION_ANSWER : "has"
    ANSWERS ||--o{ QUESTION_ANSWER : "has"
    SITEMAP_URL ||--o{ CROSSWORD_URL : "has"
    
    SITEMAP_URL {
        INTEGER sitemapurl_key pk
        TEXT sitemap_url
        BOOLEAN processed
    }
    
    CROSSWORD_URL {
        INTEGER  date_key pk
        TEXT crossword_url
        BOOLEAN processed
        DATE date
    }
    QUESTIONS {
        INTEGER question_key pk
        TEXT question
    }
    ANSWERS {
        INTEGER answer_key pk
        TEXT answer
    }
    QUESTIONS_DATE {
        INTEGER question_key fk
        INTEGER date_key fk
    }
    ANSWERS_DATE {
        INTEGER answer_key fk
        INTEGER date_key fk
    }
    QUESTION_ANSWER {
        INTEGER question_key fk
        INTEGER answer_key fk
    }
```


```pseudocode
Go to the sitemap page and get all of the sub-sitemaps that are tagged post-sitemap{\d}.xml

For each sitemap in post-sitemaps:

  Go to the sitemap page

  For each inner link with the pattern nyt-crossword-answers-/d/d-/d/d-/d/d:

    Log the link with processed:false and the stub

From the URL database, get the first row where processed is false

  
```
