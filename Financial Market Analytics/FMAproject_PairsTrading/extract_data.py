"""
One-off extraction of the sheets needed for the pairs-trading project from the
professor's .xlsm workbooks (too large / macro-enabled for pandas+openpyxl).

Parses the sheet XML in streaming mode and writes tidy CSV/Parquet caches to
./data_cache/. Run once:  python3 extract_data.py
"""
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
CACHE = ROOT / "data_cache"
CACHE.mkdir(exist_ok=True)

SPX = ROOT / "SPX500 Original.xlsm"

SECTOR_SHEETS = [
    "Energy", "Communications", "Consumer, Non-cyclical", "Industrial",
    "Financial", "Consumer, Cyclical", "Technology", "Utilities",
    "Basic Materials", "Diversified",
]

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def sheet_map(z: zipfile.ZipFile) -> dict:
    """Map sheet display name -> xl/worksheets/sheetN.xml path."""
    wb = z.read("xl/workbook.xml").decode("utf-8", "ignore")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8", "ignore")
    meta = re.findall(r'<sheet name="([^"]+)"[^>]*r:id="(rId\d+)"', wb)
    rel = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(worksheets/[^"]+)"', rels))
    return {name: "xl/" + rel[rid] for name, rid in meta if rid in rel}


def shared_strings(z: zipfile.ZipFile) -> list:
    out = []
    try:
        with z.open("xl/sharedStrings.xml") as f:
            for _, el in ET.iterparse(f):
                if el.tag == NS + "si":
                    out.append("".join(t.text or "" for t in el.iter(NS + "t")))
                    el.clear()
    except KeyError:
        pass
    return out


def col_letters_to_idx(ref: str) -> int:
    """'BC12' -> 0-based column index of 'BC'."""
    n = 0
    for ch in ref:
        if ch.isalpha():
            n = n * 26 + (ord(ch.upper()) - 64)
        else:
            break
    return n - 1


def parse_sheet(z: zipfile.ZipFile, path: str, ss: list) -> list:
    """Stream a sheet into a list of dict {col_idx: value}."""
    rows = []
    with z.open(path) as f:
        for _, el in ET.iterparse(f):
            if el.tag == NS + "row":
                vals = {}
                for c in el:
                    ref = c.attrib.get("r")
                    t = c.attrib.get("t")
                    v = None
                    for ch in c:
                        if ch.tag == NS + "v":
                            v = ch.text
                    if v is None:
                        continue
                    if t == "s":
                        v = ss[int(v)]
                    vals[col_letters_to_idx(ref)] = v
                rows.append(vals)
                el.clear()
    return rows


def to_frame(rows: list, header_row: int = 0, data_start: int = 2,
             date_col: int = 0) -> pd.DataFrame:
    """Build a DataFrame: index = dates (Excel serials in date_col),
    columns = tickers taken from header_row (col B onward)."""
    header = rows[header_row]
    tickers = {idx: name for idx, name in header.items() if idx > 0}
    cols = sorted(tickers)
    recs, dates = [], []
    for r in rows[data_start:]:
        if date_col not in r:
            continue
        try:
            serial = float(r[date_col])
        except (TypeError, ValueError):
            continue
        dates.append(serial)
        recs.append([r.get(c) for c in cols])
    df = pd.DataFrame(recs, columns=[tickers[c] for c in cols])
    df = df.apply(pd.to_numeric, errors="coerce")
    df.index = pd.to_datetime(dates, unit="D", origin="1899-12-30")
    df.index.name = "date"
    return df


def main():
    z = zipfile.ZipFile(SPX)
    smap = sheet_map(z)
    ss = shared_strings(z)
    print("Sheets:", list(smap))

    # --- names: row 2 of 'Price' has full company names ---
    rows = parse_sheet(z, smap["Price"], ss)
    header, names_row = rows[0], rows[1]
    names = pd.Series({header[i]: names_row.get(i) for i in header if i > 0},
                      name="name")
    names.index.name = "ticker"
    names.to_csv(CACHE / "spx_names.csv")

    # --- monthly prices ---
    monthly = to_frame(rows)
    monthly.to_parquet(CACHE / "spx_prices_monthly.parquet")
    print("monthly prices:", monthly.shape, monthly.index.min(), monthly.index.max())

    # --- index weights (monthly) -> membership mask ---
    peso = to_frame(parse_sheet(z, smap["Peso"], ss))
    peso.to_parquet(CACHE / "spx_weights_monthly.parquet")
    print("weights:", peso.shape)

    # --- sector membership sheets ---
    sector_of = {}
    for sec in SECTOR_SHEETS:
        if sec not in smap:
            continue
        sdf = to_frame(parse_sheet(z, smap[sec], ss))
        in_sec = (sdf.fillna(0) > 0).any()
        for tkr in in_sec[in_sec].index:
            sector_of.setdefault(tkr, sec)
        print(f"sector {sec}: {int(in_sec.sum())} tickers ever present")
    pd.Series(sector_of, name="sector").rename_axis("ticker").to_csv(
        CACHE / "spx_sectors.csv")

    # --- benchmark: 'AC' sheet has 3 (Dates, SPX Index) column pairs
    #     (daily, monthly, weekly) ---
    ac_rows = parse_sheet(z, smap["AC"], ss)
    for k, (dc, vc, label) in enumerate([(0, 1, "daily"), (2, 3, "monthly"),
                                         (4, 5, "weekly")]):
        dates, vals = [], []
        for r in ac_rows[1:]:
            if dc in r and vc in r:
                try:
                    dates.append(float(r[dc])); vals.append(float(r[vc]))
                except (TypeError, ValueError):
                    continue
        s = pd.Series(vals,
                      index=pd.to_datetime(dates, unit="D", origin="1899-12-30"),
                      name="SPX").sort_index()
        s = s[~s.index.duplicated()]
        s.rename_axis("date").to_frame().to_parquet(
            CACHE / f"spx_index_{label}.parquet")
        print(f"SPX index {label}: {len(s)} obs {s.index.min().date()} -> "
              f"{s.index.max().date()}")

    # --- daily prices (the big one, ~416 MB of XML) ---
    print("parsing 'Price daily' (this takes a few minutes)...")
    daily = to_frame(parse_sheet(z, smap["Price daily"], ss))
    daily.to_parquet(CACHE / "spx_prices_daily.parquet")
    print("daily prices:", daily.shape, daily.index.min(), daily.index.max())

    # weekly resample cache (Friday close) for the strategy
    weekly = daily.resample("W-FRI").last()
    weekly.to_parquet(CACHE / "spx_prices_weekly.parquet")
    print("weekly prices:", weekly.shape)


if __name__ == "__main__":
    main()
