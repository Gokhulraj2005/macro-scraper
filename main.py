import logging
import time
import schedule

from scraper import fetch_page, parse_table
from cleaner import clean_data, validate_data
from db import save_to_db

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run():
    logger.info("Scraper run started")
    try:
        html = fetch_page()
        if html is None:
            logger.error("Run aborted: could not fetch page")
            return

        rows = parse_table(html)
        logger.info(f"Parsed {len(rows)} country rows")

        df = clean_data(rows)
        df, issues = validate_data(df)

        saved = save_to_db(df)
        logger.info(f"Run complete: {saved} rows saved, {len(issues)} issues: {issues}")
    except ValueError as e:
        logger.error(f"Layout/validation problem: {e}")
    except Exception as e:
        logger.exception(f"Run failed: {e}")


if __name__ == "__main__":
    import sys

    if "--schedule" in sys.argv:
        run()  # run once immediately, then daily
        schedule.every().day.at("09:00").do(run)
        logger.info("Scheduler started, next run daily at 09:00")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run()