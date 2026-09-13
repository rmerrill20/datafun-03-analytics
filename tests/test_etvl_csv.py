"""tests/test_etvl_csv.py - Tests for etvl_csv.py.

WHY: Professional Python projects include tests to verify that code runs
     correctly and to catch problems early when changes are made.
     Running tests is part of the standard workflow in every module.

OBS: You do not need to read or modify this file.
     These tests create minimal CSV files in a temporary folder
     that is automatically cleaned up after each test.
"""

from pathlib import Path

"""tests/test_etvl_csv.py - Tests for etvl_csv.py.

WHY: Professional Python projects include tests to verify that code runs
     correctly and to catch problems early when changes are made.
     Running tests is part of the standard workflow in every module.

OBS: You do not need to read or modify this file.
     These tests create minimal CSV files in a temporary folder
     that is automatically cleaned up after each test.
"""

import csv
import logging

from datafun.etvl_csv import run_etvl_csv


def test_run_etvl_csv(tmp_path: Path) -> None:
    """Confirm the CSV ETVL pipeline runs and creates output."""
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    chart_file = tmp_path / "chart.png"

    with input_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["Country name", "Ladder score"],
        )
        writer.writeheader()
        writer.writerow(
            {"Country name": "Country A", "Ladder score": "5.0"}
        )
        writer.writerow(
            {"Country name": "Country B", "Ladder score": "6.0"}
        )
        writer.writerow(
            {"Country name": "Country C", "Ladder score": "7.0"}
        )

    log = logging.getLogger("test_etvl_csv")

    run_etvl_csv(
        input_file=input_file,
        output_file=output_file,
        chart_file=chart_file,
        column_name="Ladder score",
        country_column="Country name",
        log=log,
    )

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8").strip()
    assert chart_file.exists()
