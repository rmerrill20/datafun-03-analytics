"""etvl_csv.py - CSV ETVL pipeline.

Author: Ronni Merrill
Date: 2026-09-13

Practice key Python skills related to:
    - ETVL pipeline structure (Extract, Transform, Verify, Load)
    - reading CSV files using the csv module
    - keyword-only function arguments
    - error handling with raise
    - calculating statistics with the statistics module
    - writing results to a text file

OBS:
  This file is part of the working example project.
  First, run and understand the example as provided.
  When you take ownership of the project, adapt this pipeline
  to process data for your new problem.

RUN:
  No need.
  We don't usually run supporting modules like this one directly.
"""

# === DECLARE IMPORTS (BRING IN FREE CODE) ===

# === DECLARE IMPORTS (BRING IN FREE CODE) ===

import csv
import logging
from pathlib import Path

import matplotlib.pyplot as plt

from datafun.utils_etvl import (
    extract_csv_rows,
)

# === SKILL: KEYWORD-ONLY ARGUMENTS ===

# In the functions below, you will see a bare asterisk (*,) in the parameter list.
# EVERY parameter listed AFTER the asterisk must be passed by NAME when calling the function.
# This is called a keyword-only argument (or kwarg).
#
# Example:
#   def my_func(*, name: str, count: int) -> None: ...
#
#   my_func(name="case", count=3)   # correct - named arguments
#   my_func("case", 3)              # TypeError - positional not allowed
#
# WHY: In data pipelines, argument order mistakes are hard to debug.
# Named arguments make every call self-documenting.


# === SKILL: ETVL PIPELINE STRUCTURE ===

# An ETVL pipeline processes data in four steps:
#   E = Extract   - read raw data from a source (file, database, API)
#   T = Transform - clean, filter, or calculate from the raw data
#   V = Verify    - check that results are valid before writing
#   L = Load      - write the results to an output file
#
# Each step is a separate function with a single responsibility.
# This makes each step easy to test, debug, and reuse.
#
# The reusable ETVL functions are imported from utils_etvl.py.
# This module composes those functions into the CSV pipeline.


# === CALL THIS PIPELINE FROM app.py ===

# The main app.py file declares the data-specific choices:
#
#   CSV_INPUT   = data/raw/2020_happiness.csv
#   CSV_OUTPUT  = data/processed/csv_ladder_score_stats.txt
#   CSV_COLUMN  = Ladder score
#   CSV_GRAIN   = one country
#
# app.py calls this function and passes those values in:
#
#   run_etvl_csv(
#       input_file=CSV_INPUT,
#       output_file=CSV_OUTPUT,
#       column_name=CSV_COLUMN,
#       grain=CSV_GRAIN,
#       log=LOG,
#   )
#
# Each named argument provides one value this function needs:
#
#   input_file  = the CSV file to read
#   output_file = the text file to write
#   column_name = the numeric column to analyze
#   grain       = what one row represents
#   log         = where to send progress messages
#
# Notice that the names on the LEFT belong to this function.
# The values on the RIGHT are declared in app.py.
#
# These are keyword-only arguments.
# The * below means each argument must be passed by name.


# === FULL PIPELINE ===

# This function composes the four steps into a single callable pipeline.
# Each step receives the output of the previous step.
# The logger is passed in as an argument so this function works in any context.


def analyze_above_average_happiness(
    *,
    rows: list[dict[str, str]],
    country_column: str,
    score_column: str,
    log: logging.Logger,
) -> tuple[float, list[dict[str, str]]]:
    """Calculate average happiness and find countries above the average."""

    scores = []

    for row in rows:
        try:
            score = float(row[score_column])
            scores.append(score)
        except KeyError, ValueError:
            continue

    if not scores:
        raise ValueError("No valid happiness scores were found.")

    average_score = sum(scores) / len(scores)

    above_average = []

    for row in rows:
        try:
            score = float(row[score_column])

            if score > average_score:
                above_average.append(
                    {
                        country_column: row[country_column],
                        score_column: row[score_column],
                    }
                )
        except KeyError, ValueError:
            continue

    above_average.sort(
        key=lambda row: float(row[score_column]),
        reverse=True,
    )

    log.info("Average happiness score: %.2f", average_score)
    log.info("Countries above average: %d", len(above_average))

    return average_score, above_average


def save_above_average_results(
    *,
    results: list[dict[str, str]],
    country_column: str,
    score_column: str,
    output_file: Path,
    log: logging.Logger,
) -> None:
    """Save countries above the average happiness score."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[country_column, score_column],
        )

        writer.writeheader()
        writer.writerows(results)

    log.info("Saved above-average results to %s", output_file)


def create_happiness_chart(
    *,
    results: list[dict[str, str]],
    country_column: str,
    score_column: str,
    chart_file: Path,
    log: logging.Logger,
) -> None:
    """Create a chart of the top 10 countries above average."""

    top_10 = results[:10]

    countries = [row[country_column] for row in reversed(top_10)]

    scores = [float(row[score_column]) for row in reversed(top_10)]

    chart_file.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))

    plt.barh(countries, scores)

    plt.xlabel("Happiness Score")
    plt.ylabel("Country")
    plt.title("Top 10 Countries Above Average Happiness Score")

    plt.tight_layout()

    plt.savefig(chart_file, dpi=150)
    plt.close()

    log.info("Saved happiness chart to %s", chart_file)


def run_etvl_csv(
    *,
    input_file: Path,
    output_file: Path,
    chart_file: Path,
    column_name: str,
    country_column: str,
    log: logging.Logger,
) -> None:
    """Run the full CSV ETVL pipeline.

    Arguments:
        input_file: Path to the input CSV file.
        output_file: Path to the output text file.
        chart_file: Path to the output chart file.
        column_name: Name of the numeric column to summarize.
        country_column: Name of the country column.
        log: Logger for logging messages.

    Returns:
        None.
    """
    log.info("CSV: START")

    # === E: EXTRACT ===

    # csv.DictReader reads each row as a dictionary keyed by column name.
    # This makes it easy to access columns by name rather than by index.
    #
    # Defensive programming: always check that a file exists before reading it.
    # Always check that expected data is available before accessing it.
    # Use raise to signal an error the caller must handle.

    rows = extract_csv_rows(
        file_path=input_file,
        log=log,
    )

    # === T: TRANSFORM ===

    # First convert the selected column from raw strings to numeric values.
    # Empty and non-numeric values are skipped.

    average_score, above_average = analyze_above_average_happiness(
        rows=rows,
        country_column=country_column,
        score_column=column_name,
        log=log,
    )

    # The statistics module provides mean() and stdev().
    # stdev() requires at least two values - guard against a single-value list.

    # === V: VERIFY ===

    # Verification catches problems between Transform and Load.
    # It is cheaper to detect a bad result before writing it to disk.
    # Use raise to signal an error the caller must handle.

    if not above_average:
        raise ValueError("No countries were found above the average happiness score.")

    log.info(
        "Verified %d countries above the average score of %.2f",
        len(above_average),
        average_score,
    )

    # === L: LOAD ===

    # Path.open("w") creates or overwrites a file.
    # Always create parent directories before writing
    # with mkdir(parents=True, exist_ok=True).
    # Use f-strings to format numeric output
    # to a consistent number of decimal places.

    save_above_average_results(
        results=above_average,
        country_column=country_column,
        score_column=column_name,
        output_file=output_file,
        log=log,
    )

    create_happiness_chart(
        results=above_average,
        country_column=country_column,
        score_column=column_name,
        chart_file=chart_file,
        log=log,
    )

    log.info("CSV: wrote %s", output_file)
    log.info("CSV: END")
