import logging
import pandas as pd

logger = logging.getLogger(__name__)


def clean_data(rows):
    df = pd.DataFrame(rows)

    # Remove footnotes like [1] and extra spaces from country names
    df["Country"] = df["Country"].str.replace(r"\[.*?\]", "", regex=True).str.strip()

    # Wide -> long: one row per country per year
    long_df = df.melt(id_vars="Country", var_name="year", value_name="inflation_rate")
    long_df = long_df.rename(columns={"Country": "country"})

    # Clean values: special minus sign, footnotes, % symbol
    long_df["inflation_rate"] = (
        long_df["inflation_rate"]
        .astype(str)
        .str.replace("−", "-", regex=False)
        .str.replace(r"\[.*?\]", "", regex=True)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    long_df["inflation_rate"] = pd.to_numeric(long_df["inflation_rate"], errors="coerce")
    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce").astype("Int64")

    long_df = long_df.drop_duplicates(subset=["country", "year"])
    return long_df


def validate_data(df, min_countries=100):
    issues = []

    n_countries = df["country"].nunique()
    if n_countries < min_countries:
        issues.append(f"Only {n_countries} countries found (expected >= {min_countries})")

    null_count = int(df["inflation_rate"].isna().sum())
    if null_count > 0:
        issues.append(f"{null_count} missing inflation values (dropped)")

    out_of_range = df[(df["inflation_rate"] < -50) | (df["inflation_rate"] > 1000)]
    if not out_of_range.empty:
        issues.append(f"{len(out_of_range)} out-of-range values")

    for issue in issues:
        logger.warning(issue)

    return df.dropna(subset=["inflation_rate"]), issues


if __name__ == "__main__":
    from scraper import fetch_page, parse_table

    df = clean_data(parse_table(fetch_page()))
    df, issues = validate_data(df)
    print(df.head(10))
    print("Rows:", len(df))
    print("Issues:", issues)