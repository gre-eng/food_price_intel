"""
Loader for the NBS "Selected Food Price Watch" monthly xlsx files.

Verified real structure (checked directly against all 16 uploaded files,
Jan 2025 - Apr 2026):
  - Each file has exactly 2 sheets.
  - One sheet is always named exactly "Zone All item" -> zone breakdown,
    columns: Item Label, NORTH CENTRAL, NORTH EAST, NORTH WEST, SOUTH EAST,
    SOUTH SOUTH, SOUTH WEST.
  - The other sheet (name varies, and in 2 of the 16 files the sheet tab name
    is mislabeled "Selected Food Dec 2024" even though the data is for a
    different month) has columns: Item Label, Average of <PrevYearMonth>,
    Average of <PrevMonth>, Average of <CurrentMonth>, MoM, YoY, Highest, Lowest.

  Because the sheet TAB NAME is unreliable, this loader:
    1. Picks the sheet that is NOT "Zone All item" for national-level data.
    2. Reads the actual report month from the 4th column header
       (e.g. "Average of Apr-25" or "Average of April-26"), not from the
       sheet tab name or the filename.
"""

import re
import glob
import openpyxl
import pandas as pd
from datetime import datetime
from utils.commodity_mapper import map_commodity

MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}


def parse_report_month(header_text: str):
    """
    Extract (year, month) from a header like 'Average of Apr-25' or
    'Average of April-26'. Returns None if the pattern isn't recognized.
    """
    if not header_text:
        return None
    match = re.search(r"of\s+([A-Za-z]+)[-\s](\d{2,4})", str(header_text))
    if not match:
        return None
    month_str, year_str = match.groups()
    month = MONTH_MAP.get(month_str.lower())
    if month is None:
        return None
    year = int(year_str)
    if year < 100:
        year += 2000
    return year, month


def load_one_nbs_file(path: str):
    """
    Returns a tuple: (national_df, zone_df, report_year, report_month)
    national_df columns: item_label, price, source_file
    zone_df columns: item_label, zone, price, source_file
    """
    wb = openpyxl.load_workbook(path, data_only=True)
    zone_sheet_name = "Zone All item"
    other_sheets = [s for s in wb.sheetnames if s != zone_sheet_name]
    if not other_sheets:
        raise ValueError(f"No national-level sheet found in {path}")
    national_ws = wb[other_sheets[0]]

    header = [c.value for c in national_ws[1]]
    if len(header) < 4:
        raise ValueError(f"Unexpected header shape in {path}: {header}")

    report = parse_report_month(header[3])
    if report is None:
        raise ValueError(f"Could not parse report month from header '{header[3]}' in {path}")
    report_year, report_month = report

    national_rows = []
    for row in national_ws.iter_rows(min_row=2, values_only=True):
        item_label = row[0]
        current_value = row[3]
        if item_label is None or current_value is None:
            continue
        national_rows.append({
            "item_label": str(item_label).strip(),
            "price": current_value,
            "source_file": path.split("/")[-1].split("\\")[-1],
        })
    national_df = pd.DataFrame(national_rows)

    zone_rows = []
    if zone_sheet_name in wb.sheetnames:
        zone_ws = wb[zone_sheet_name]
        zone_header = [c.value for c in zone_ws[1]]
        zone_names = zone_header[1:]
        for row in zone_ws.iter_rows(min_row=2, values_only=True):
            item_label = row[0]
            if item_label is None:
                continue
            for zone_name, value in zip(zone_names, row[1:]):
                if zone_name is None or value is None:
                    continue
                zone_rows.append({
                    "item_label": str(item_label).strip(),
                    "zone": str(zone_name).strip(),
                    "price": value,
                    "source_file": path.split("/")[-1].split("\\")[-1],
                })
    zone_df = pd.DataFrame(zone_rows)

    return national_df, zone_df, report_year, report_month


def load_all_nbs(directory: str) -> pd.DataFrame:
    """
    Load every xlsx in `directory`, tag each with its real report date
    (parsed from the column header, not the filename), and concatenate.
    """
    files = sorted(glob.glob(f"{directory}/*.xlsx"))
    all_rows = []
    errors = []
    for f in files:
        try:
            national_df, _, year, month = load_one_nbs_file(f)
            national_df["date"] = datetime(year, month, 1)
            all_rows.append(national_df)
        except ValueError as e:
            errors.append(str(e))

    if errors:
        print("NBS load warnings:", errors)

    if not all_rows:
        return pd.DataFrame(columns=["date", "item_label", "commodity_canonical", "price", "source_file"])

    combined = pd.concat(all_rows, ignore_index=True)
    combined["commodity_canonical"] = combined["item_label"].apply(lambda x: map_commodity(x, "nbs"))
    combined["source"] = "NBS"
    return combined


def get_unmapped_nbs_commodities(df: pd.DataFrame) -> list:
    """Real unique item labels present in the loaded files that are not in our verified crosswalk."""
    return sorted(
        n for n in df["item_label"].dropna().unique()
        if map_commodity(n, "nbs") is None
    )


def filter_mapped(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["commodity_canonical"].notna()].copy()