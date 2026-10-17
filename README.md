# Macroeconomic Indicators Web Scraper

A Python pipeline that scrapes country-level inflation data from Wikipedia, cleans and validates it, and stores it in a SQL database. It includes retry handling, layout-change detection, run logging, and daily scheduling.

## Overview

The pipeline runs five stages:

1. **Fetch**: downloads the page with Requests, using a timeout, a User-Agent header, and retries with exponential backoff.
2. **Parse**: extracts the HTML table with BeautifulSoup. It raises an error if the table or its headers are missing, which signals a site layout change.
3. **Clean**: uses Pandas to remove footnote markers like `[1]`, convert the special minus sign (−), convert text to numbers, and reshape the wide table (one column per year) into long format (country, year, rate).
4. **Validate**: checks the country count, missing values, and out-of-range values, and logs any issues.
5. **Store**: saves records to SQLite with an upsert, so repeated runs update existing rows instead of creating duplicates.

## Features

- Retry logic with exponential backoff for failed requests
- Layout-change detection (missing table or unexpected headers)
- Data validation with logged warnings
- Duplicate-safe storage using `ON CONFLICT ... DO UPDATE`
- Run logging to `scraper.log`
- Optional daily scheduling

## Tech Stack

Python, Requests, BeautifulSoup, Pandas, SQLite, schedule, logging, Git

## Project Structure

```
macro-scraper/
├── scraper.py          # fetch and parse
├── cleaner.py          # clean and validate
├── db.py               # SQLite storage (upsert)
├── main.py             # pipeline, logging, scheduling
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone https://github.com/Gokhulraj2005/macro-scraper.git
cd macro-scraper
python -m venv venv
venv\Scripts\activate        # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

## Usage

Run the pipeline once:

```bash
python main.py
```

Run it now, then repeat daily at 09:00:

```bash
python main.py --schedule
```

For unattended runs, use Windows Task Scheduler (or cron on Linux/macOS) to run `python main.py` daily.

Each module can also be tested on its own:

```bash
python scraper.py    # fetch and parse test
python cleaner.py    # cleaning and validation test
python db.py         # full pipeline into the database
```

## Sample Output

Log file (`scraper.log`):

```
INFO - Scraper run started
INFO - Parsed 189 country rows
WARNING - 104 missing inflation values (dropped)
INFO - Run complete: 1786 rows saved, 1 issues: ['104 missing inflation values (dropped)']
```

Result: 189 countries parsed and 1,786 country-year records stored for 2015 to 2024. Blank source cells (104) were detected by validation and dropped.

Check the database:

```bash
python -c "import sqlite3; print(sqlite3.connect('macro.db').execute('SELECT * FROM inflation LIMIT 5').fetchall())"
```

## Challenges and Solutions

| Challenge | Solution |
|---|---|
| Wikipedia uses a special minus sign (−) and footnote markers like `[1]`, which broke numeric conversion | Normalised both before converting to numbers |
| The table has one column per year, which is awkward for SQL queries | Reshaped to long format (country, year, rate) |
| Blank cells in the source | Logged as validation warnings instead of disappearing silently |
| Daily re-runs could create duplicate rows | Added a unique key on (country, year) and an upsert |
| The site layout could change without notice | Parser checks the table and headers, then logs the error and stops instead of saving bad data |

## Future Improvements

- Add more sources (exchange rates, interest rates) with different page structures
- Add MySQL support
- Add XPath-based extraction with `lxml`
- Add unit tests with `pytest`
- Send an alert (email or message) when a run fails

## Data Source and Disclaimer

Data comes from Wikipedia's "List of countries by inflation rate" page. This is a learning project. Check the source site's terms before reusing the data.

## Author

**Gokhul Raj V**
[LinkedIn](https://linkedin.com/in/gokhul-raj-8b4630291) | [GitHub](https://github.com/Gokhulraj2005) | gokhulrajvelu.2005@gmail.com
