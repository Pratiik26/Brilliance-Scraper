# """
# Brilliance.com diamond scraper (lab-grown + natural), single-file version.

# Setup:
#     pip install curl_cffi pandas

#     Then fill in the COOKIES dict below with values copied from your
#     browser's DevTools (Network tab -> a request to worker.brilliance.com
#     -> Headers -> Cookie, or Application tab -> Cookies).

# Run:
#     python brilliance_scraper_single.py

# Output (written incrementally, page by page, not just at the end):
#     diamonds_lab.csv
#     diamonds_natural.csv
#     diamonds_all.csv   (combined, written after both finish)
# """

# """
# Brilliance.com diamond scraper (lab-grown + natural), single-file version.

# Setup:
#     pip install curl_cffi pandas

#     Then fill in the COOKIES dict below with values copied from your
#     browser's DevTools (Network tab -> a request to worker.brilliance.com
#     -> Headers -> Cookie, or Application tab -> Cookies).

# Run:
#     python brilliance_scraper_single.py

# Output (written incrementally, page by page, not just at the end):
#     diamonds_lab.csv       - all shapes, lab-grown diamonds
#     diamonds_natural.csv   - all shapes, natural diamonds
#     diamonds_all.csv       - both combined, written after both finish

# Resume support:
#     If you stop and re-run the script, each shape resumes from the last
#     page already saved for that shape + diamond type in the CSV, instead
#     of starting over from page 0.
# """

# from curl_cffi import requests
# import pandas as pd
# import csv
# import os
# import time
# import random

# # ---------------------------------------------------------------------------
# # COOKIES - paste what you copied from DevTools here.
# # Only include the ones you actually have.
# # ---------------------------------------------------------------------------
# COOKIES = {
#     "__cf_bm": "Ix47zaYU_ZnKoJ2sYKEFBlKmYz0GOEYe6VhioK3bhHQ-1784805006.5444055-1.0.1.1-9S85HwrDK3ETqJS.Pl3TTELgMsws7MtMbqeZcP39A_UkDvu8UkroO.ixuwBnH2W175lI51Xwm6uddrrp0wiLFyuYPTC6eODGfxlT8ma7gWfDbrAO4ndCsACVgLPPPIn7zADnPabYTLODKzCRXUiL9A",
#     # "cf_clearance": "PASTE_IF_YOU_HAVE_IT",
#     # "session_id": "PASTE_IF_YOU_HAVE_IT",
# }

# LAB_URL = "https://worker.brilliance.com/api/v1/lab-grown-diamond-search"
# NATURAL_URL = "https://worker.brilliance.com/api/v1/diamond-search"

# HEADERS = {
#     "Accept": "application/json, text/plain, */*",
#     "Content-Type": "application/json",
#     "Referer": "https://www.brilliance.com/",
#     "User-Agent":
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/149 Safari/537.36"
# }

# SHAPES = {
#     "ROUND": 0,
#     "PRINCESS": 1,
#     "CUSHION": 2,
#     "OVAL": 3,
#     "EMERALD": 4,
#     "HEART": 5,
#     "PEAR": 6,
#     "MARQUISE": 7,
#     "ASSCHER": 8,
#     "RADIANT": 9,
# }

# LAB_FILTERS = {
#     "priceMin": 750,
#     "priceMax": 100000,
#     "caratMin": 1.5,
#     "caratMax": 12,
#     "colorMin": 6,
#     "colorMax": 9,
#     "clarityMin": 4,
#     "clarityMax": 9,
# }

# NATURAL_FILTERS = {
#     "priceMin": 750,
#     "priceMax": 350000,
#     "caratMin": 0.5,
#     "caratMax": 10,
#     "colorMin": 0,
#     "colorMax": 9,
#     "clarityMin": 0,
#     "clarityMax": 9,
# }

# # Column order used for every CSV written by this script.
# CSV_COLUMNS = [
#     "ID", "Shape", "Price", "List Price", "Carat", "Color", "Clarity", "Cut",
#     "Report", "Report Number", "Polish", "Symmetry", "Depth", "Table",
#     "Fluorescence", "Girdle", "Culet", "Measurement", "Lengthtow",
#     "Alias URL", "Node URL", "Type", "ShapeName",
# ]

# PER_PAGE = 48  # rows returned per API page


# # ---------------------------------------------------------------------------
# # API request helpers
# # ---------------------------------------------------------------------------

# def build_payload(shape_id, pager, filters):
#     return {
#         "data": {
#             "imgOnly": True,
#             "view": "grid",
#             "priceMin": filters["priceMin"],
#             "priceMax": filters["priceMax"],
#             "caratMin": filters["caratMin"],
#             "caratMax": filters["caratMax"],
#             "colorMin": filters["colorMin"],
#             "colorMax": filters["colorMax"],
#             "clarityMin": filters["clarityMin"],
#             "clarityMax": filters["clarityMax"],
#             "depthMin": 0,
#             "depthMax": 90,
#             "tableMin": 0,
#             "tableMax": 90,
#             "shapeList": [shape_id],
#             "certificateList": [],
#             "pager": pager,
#             "cutMin": 0,
#             "cutMax": 4,
#             "polishMin": 0,
#             "polishMax": 3,
#             "symmetryMin": 0,
#             "symmetryMax": 3,
#             "fluorMin": 0,
#             "fluorMax": 3,
#             "fastShipping": 0,
#         }
#     }


# def fetch_batch(url, shape_id, pager, filters, result_key):

#     payload = build_payload(shape_id, pager, filters)
#     retries = 8

#     for attempt in range(retries):
#         try:
#             response = requests.post(
#                 url,
#                 headers=HEADERS,
#                 cookies=COOKIES,
#                 json=payload,
#                 impersonate=random.choice(["chrome123"]),
#                 timeout=30,
#             )

#             print(f"Pager {pager} | Status {response.status_code} | Attempt {attempt + 1}")

#             if response.status_code == 200:
#                 try:
#                     result = response.json()
#                 except Exception:
#                     print("Invalid JSON response")
#                     print(response.text[:500])
#                     time.sleep(2)
#                     continue
#                 diamonds = result.get(result_key, [])
#                 print("Returned:", len(diamonds))
#                 return diamonds

#             elif response.status_code == 429:
#                 wait = min(30, (2 ** attempt) + random.uniform(0.5, 2))
#                 print(f"429 received. Sleeping {wait:.1f} seconds...")
#                 time.sleep(wait)
#                 continue

#             elif response.status_code in (500, 502, 503, 504):
#                 wait = random.uniform(2, 4)
#                 print(f"Server error. Waiting {wait:.1f}s")
#                 time.sleep(wait)
#                 continue

#             else:
#                 print(response.text[:500])
#                 return []

#         except Exception as e:
#             wait = random.uniform(5, 10)
#             print(e)
#             print(f"Retrying in {wait:.1f}s")
#             time.sleep(wait)

#     return []


# # ---------------------------------------------------------------------------
# # Row / CSV helpers
# # ---------------------------------------------------------------------------

# def row_from_diamond(d):
#     return {
#         "ID": d.get("nid"),
#         "Shape": d.get("shape"),
#         "Price": d.get("price"),
#         "List Price": d.get("list_price"),
#         "Carat": d.get("carat"),
#         "Color": d.get("color"),
#         "Clarity": d.get("clarity"),
#         "Cut": d.get("cut"),
#         "Report": d.get("report"),
#         "Report Number": d.get("reportNumber"),
#         "Polish": d.get("polish"),
#         "Symmetry": d.get("symmetry"),
#         "Depth": d.get("depth"),
#         "Table": d.get("table"),
#         "Fluorescence": d.get("fluorescence"),
#         "Girdle": d.get("girdle"),
#         "Culet": d.get("culet"),
#         "Measurement": d.get("measurement"),
#         "Lengthtow": d.get("lengthtow"),
#         "Alias URL": d.get("alias"),
#         "Node URL": d.get("url"),
#     }


# def ensure_header(filepath):
#     """If filepath already exists and has data but its first line isn't
#     the expected header row, prepend the header."""
#     if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
#         return

#     expected_header = ",".join(CSV_COLUMNS)

#     with open(filepath, "r", newline="", encoding="utf-8") as f:
#         first_line = f.readline().strip()

#     if first_line != expected_header:
#         print(f"{filepath} is missing its header row - adding it now.")
#         with open(filepath, "r", newline="", encoding="utf-8") as f:
#             content = f.read()
#         with open(filepath, "w", newline="", encoding="utf-8") as f:
#             f.write(expected_header + "\n" + content)


# def load_existing_ids(filepath):
#     """IDs already saved in filepath, so we don't write duplicates."""
#     ids = set()
#     if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
#         try:
#             existing = pd.read_csv(filepath, usecols=["ID"])
#             ids = set(existing["ID"].dropna().astype(str))
#         except Exception as e:
#             print(f"Could not read existing IDs from {filepath}: {e}")
#     return ids


# def write_rows_to_csv(rows, filepath):
#     """Append rows to filepath, writing the header first only if the
#     file doesn't exist yet or is empty."""
#     if not rows:
#         return
#     need_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
#     with open(filepath, "a", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
#         if need_header:
#             writer.writeheader()
#         writer.writerows(rows)


# def get_start_pager(output_file, diamond_type, shape_name, per_page=PER_PAGE):
#     """Resume support: how many pages of this exact (diamond_type,
#     shape_name) are already saved in output_file? Return the next
#     pager to fetch. Works for any shape/type, not just one hardcoded
#     combination."""
#     if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
#         return 0
#     try:
#         df = pd.read_csv(output_file)
#         count = ((df["Type"] == diamond_type) & (df["ShapeName"] == shape_name)).sum()
#     except Exception as e:
#         print(f"Could not determine resume point from {output_file}: {e}")
#         return 0
#     return int(count // per_page)


# # ---------------------------------------------------------------------------
# # Scraping
# # ---------------------------------------------------------------------------

# def scrape_shape(url, shape_id, filters, result_key, diamond_type, shape_name,
#                   output_file, seen_ids):
#     """Fetch page by page and write each page's rows to output_file as
#     soon as they arrive. Resumes from the last saved page for this
#     specific shape + diamond type."""

#     pager = get_start_pager(output_file, diamond_type, shape_name)
#     total_written = 0

#     if pager > 0:
#         print(f"Resuming {diamond_type}/{shape_name} at page {pager}")

#     while True:
#         batch = fetch_batch(url, shape_id, pager, filters, result_key)

#         if not batch:
#             print("No more diamonds for this shape")
#             break

#         rows = []
#         for d in batch:
#             row = row_from_diamond(d)
#             row["Type"] = diamond_type
#             row["ShapeName"] = shape_name

#             diamond_id = str(row["ID"])
#             if diamond_id in seen_ids:
#                 continue
#             seen_ids.add(diamond_id)
#             rows.append(row)

#         write_rows_to_csv(rows, output_file)

#         total_written += len(rows)
#         print(f"Page {pager}: {len(rows)} new rows written "
#               f"(total so far for this shape: {total_written})")

#         pager += 1
#         time.sleep(random.uniform(0.8, 1.8))

#     return total_written


# def scrape_diamonds(diamond_type, output_file, shapes=None):
#     """
#     diamond_type: "lab" or "natural"
#     output_file: CSV path to write to (rows are appended page by page)
#     shapes: list of shape names from SHAPES, defaults to all shapes
#     """
#     if diamond_type == "lab":
#         url = LAB_URL
#         filters = LAB_FILTERS
#         result_key = "diamond"
#     elif diamond_type == "natural":
#         url = NATURAL_URL
#         filters = NATURAL_FILTERS
#         result_key = "diamond"
#     else:
#         raise ValueError("diamond_type must be 'lab' or 'natural'")

#     shapes = shapes or list(SHAPES.keys())

#     ensure_header(output_file)
#     seen_ids = load_existing_ids(output_file)
#     print(f"Resuming with {len(seen_ids)} IDs already in {output_file}")

#     grand_total = 0
#     for shape in shapes:
#         print(f"\n=== {diamond_type.upper()} - {shape} ===")
#         shape_id = SHAPES[shape]
#         written = scrape_shape(
#             url, shape_id, filters, result_key,
#             diamond_type, shape, output_file, seen_ids,
#         )
#         grand_total += written

#     return grand_total


# if __name__ == "__main__":

#     LAB_CSV = "diamonds_lab.csv"
#     NATURAL_CSV = "diamonds_natural.csv"
#     ALL_CSV = "diamonds_all.csv"

#     lab_total = scrape_diamonds("lab", LAB_CSV)
#     print(f"\nSaved {lab_total} new lab-grown diamonds -> {LAB_CSV}")

#     natural_total = scrape_diamonds("natural", NATURAL_CSV)
#     print(f"Saved {natural_total} new natural diamonds -> {NATURAL_CSV}")

#     # Combine both files into diamonds_all.csv at the end.
#     frames = []
#     if os.path.exists(LAB_CSV):
#         frames.append(pd.read_csv(LAB_CSV))
#     if os.path.exists(NATURAL_CSV):
#         frames.append(pd.read_csv(NATURAL_CSV))

#     if frames:
#         all_df = pd.concat(frames, ignore_index=True)
#         all_df = all_df.drop_duplicates(subset=["ID"])
#         all_df.to_csv(ALL_CSV, index=False)
#         print(f"Saved {len(all_df)} total diamonds -> {ALL_CSV}")

#claude code which is working and resuming from where stopped.

"""
Brilliance.com diamond scraper (lab-grown + natural), single-file version.

Setup:
    pip install curl_cffi pandas

    Then fill in the COOKIES dict below with values copied from your
    browser's DevTools (Network tab -> a request to worker.brilliance.com
    -> Headers -> Cookie, or Application tab -> Cookies).

Run:
    python self.py

Output (written incrementally, page by page, not just at the end):
    diamonds_lab.csv       - all shapes, lab-grown diamonds
    diamonds_natural.csv   - all shapes, natural diamonds
    diamonds_all.csv       - both combined, written after both finish

Resume support:
    If you stop and re-run the script, each shape resumes from the last
    page already saved for that shape + diamond type in the CSV, instead
    of starting over from page 0.

End-of-data detection:
    Some backends don't return an empty list once you page past the end
    of real results - they just keep re-serving the same (or a clamped)
    page over and over, always with a full batch of "diamonds" that are
    all already in your CSV. This script tracks that: if a page comes
    back with 0 NEW rows (all duplicates) for MAX_CONSECUTIVE_DUPE_PAGES
    pages in a row, it treats that as the true end of data for that
    shape and moves on, instead of looping forever.
"""

from curl_cffi import requests
import pandas as pd
import csv
import os
import time
import random

# ---------------------------------------------------------------------------
# COOKIES - paste what you copied from DevTools here.
# Only include the ones you actually have. Include cf_clearance if present -
# it matters more than __cf_bm for passing the bot check, and both expire,
# so refresh these whenever the script starts getting blocked/looping.
# ---------------------------------------------------------------------------
COOKIES = {
    "__cf_bm": "XsE.WU7FhaDfp9T9qgBgz4YmvlcQnR7guL3KZKsFTI4-1784543247.811991-1.0.1.1-MazWy_Df69EghsmLGpZtNSxTO3G.qYOllRM8h4rLlCkvFddD1vr8sKcfaTlR057uZexFa2OcVfWczRbL7sHtLU1MvQl0l6TV0QhZBBH3t0u3wKHY_WecSZicsiFUfiT1O1hB5HKyZkRKD2_5xbZk9A",
    # "cf_clearance": "PASTE_IF_YOU_HAVE_IT",
    # "session_id": "PASTE_IF_YOU_HAVE_IT",
}

LAB_URL = "https://worker.brilliance.com/api/v1/lab-grown-diamond-search"
NATURAL_URL = "https://worker.brilliance.com/api/v1/diamond-search"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://www.brilliance.com/",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/149 Safari/537.36"
}

SHAPES = {
    "ROUND": 0,
    "PRINCESS": 1,
    "CUSHION": 2,
    "OVAL": 3,
    "EMERALD": 4,
    "HEART": 5,
    "PEAR": 6,
    "MARQUISE": 7,
    "ASSCHER": 8,
    "RADIANT": 9,
}

LAB_FILTERS = {
    "priceMin": 750,
    "priceMax": 100000,
    "caratMin": 1.5,
    "caratMax": 12,
    "colorMin": 6,
    "colorMax": 9,
    "clarityMin": 4,
    "clarityMax": 9,
}

NATURAL_FILTERS = {
    "priceMin": 750,
    "priceMax": 350000,
    "caratMin": 0.5,
    "caratMax": 10,
    "colorMin": 0,
    "colorMax": 9,
    "clarityMin": 0,
    "clarityMax": 9,
}

# Column order used for every CSV written by this script.
CSV_COLUMNS = [
    "ID", "Shape", "Price", "List Price", "Carat", "Color", "Clarity", "Cut",
    "Report", "Report Number", "Polish", "Symmetry", "Depth", "Table",
    "Fluorescence", "Girdle", "Culet", "Measurement", "Lengthtow",
    "Alias URL", "Node URL", "Type", "ShapeName",
]

PER_PAGE = 48  # rows returned per API page

# How many consecutive pages of 100%-duplicate results we tolerate before
# concluding a shape is exhausted and moving on. Set to 1 if you want to
# stop immediately on the first all-duplicate page instead.
MAX_CONSECUTIVE_DUPE_PAGES = 3


# ---------------------------------------------------------------------------
# API request helpers
# ---------------------------------------------------------------------------

def build_payload(shape_id, pager, filters):
    return {
        "data": {
            "imgOnly": True,
            "view": "grid",
            "priceMin": filters["priceMin"],
            "priceMax": filters["priceMax"],
            "caratMin": filters["caratMin"],
            "caratMax": filters["caratMax"],
            "colorMin": filters["colorMin"],
            "colorMax": filters["colorMax"],
            "clarityMin": filters["clarityMin"],
            "clarityMax": filters["clarityMax"],
            "depthMin": 0,
            "depthMax": 90,
            "tableMin": 0,
            "tableMax": 90,
            "shapeList": [shape_id],
            "certificateList": [],
            "pager": pager,
            "cutMin": 0,
            "cutMax": 4,
            "polishMin": 0,
            "polishMax": 3,
            "symmetryMin": 0,
            "symmetryMax": 3,
            "fluorMin": 0,
            "fluorMax": 3,
            "fastShipping": 0,
        }
    }


def fetch_batch(url, shape_id, pager, filters, result_key):

    payload = build_payload(shape_id, pager, filters)
    retries = 8

    for attempt in range(retries):
        try:
            response = requests.post(
                url,
                headers=HEADERS,
                cookies=COOKIES,
                json=payload,
                impersonate=random.choice(["chrome123"]),
                timeout=30,
            )

            print(f"Pager {pager} | Status {response.status_code} | Attempt {attempt + 1}")

            if response.status_code == 200:
                try:
                    result = response.json()
                except Exception:
                    print("Invalid JSON response (likely a Cloudflare challenge page)")
                    print(response.text[:500])
                    time.sleep(2)
                    continue

                # If the API exposes a total count, surface it - useful for
                # sanity-checking whether you've actually reached the end.
                for total_key in ("total", "totalCount", "resultCount", "count"):
                    if total_key in result:
                        print(f"API reports '{total_key}': {result[total_key]}")
                        break

                diamonds = result.get(result_key, [])
                print("Returned:", len(diamonds))
                return diamonds

            elif response.status_code == 403:
                print("403 Forbidden - cookies are almost certainly expired/invalid.")
                print("Refresh COOKIES from browser DevTools and re-run.")
                time.sleep(3)
                continue

            elif response.status_code == 429:
                wait = min(30, (2 ** attempt) + random.uniform(0.5, 2))
                print(f"429 received. Sleeping {wait:.1f} seconds...")
                time.sleep(wait)
                continue

            elif response.status_code in (500, 502, 503, 504):
                wait = random.uniform(2, 4)
                print(f"Server error. Waiting {wait:.1f}s")
                time.sleep(wait)
                continue

            else:
                print(response.text[:500])
                return []

        except Exception as e:
            wait = random.uniform(5, 10)
            print(e)
            print(f"Retrying in {wait:.1f}s")
            time.sleep(wait)

    return []


# ---------------------------------------------------------------------------
# Row / CSV helpers
# ---------------------------------------------------------------------------

def row_from_diamond(d):
    return {
        "ID": d.get("nid"),
        "Shape": d.get("shape"),
        "Price": d.get("price"),
        "List Price": d.get("list_price"),
        "Carat": d.get("carat"),
        "Color": d.get("color"),
        "Clarity": d.get("clarity"),
        "Cut": d.get("cut"),
        "Report": d.get("report"),
        "Report Number": d.get("reportNumber"),
        "Polish": d.get("polish"),
        "Symmetry": d.get("symmetry"),
        "Depth": d.get("depth"),
        "Table": d.get("table"),
        "Fluorescence": d.get("fluorescence"),
        "Girdle": d.get("girdle"),
        "Culet": d.get("culet"),
        "Measurement": d.get("measurement"),
        "Lengthtow": d.get("lengthtow"),
        "Alias URL": d.get("alias"),
        "Node URL": d.get("url"),
    }


def ensure_header(filepath):
    """If filepath already exists and has data but its first line isn't
    the expected header row, prepend the header."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return

    expected_header = ",".join(CSV_COLUMNS)

    with open(filepath, "r", newline="", encoding="utf-8") as f:
        first_line = f.readline().strip()

    if first_line != expected_header:
        print(f"{filepath} is missing its header row - adding it now.")
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            content = f.read()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(expected_header + "\n" + content)


def load_existing_ids(filepath):
    """IDs already saved in filepath, so we don't write duplicates."""
    ids = set()
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        try:
            existing = pd.read_csv(filepath, usecols=["ID"], low_memory=False)
            ids = set(existing["ID"].dropna().astype(str))
        except Exception as e:
            print(f"Could not read existing IDs from {filepath}: {e}")
    return ids


def write_rows_to_csv(rows, filepath):
    """Append rows to filepath, writing the header first only if the
    file doesn't exist yet or is empty."""
    if not rows:
        return
    need_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if need_header:
            writer.writeheader()
        writer.writerows(rows)


def get_start_pager(output_file, diamond_type, shape_name, per_page=PER_PAGE):
    """Resume support: how many pages of this exact (diamond_type,
    shape_name) are already saved in output_file? Return the next
    pager to fetch. Works for any shape/type, not just one hardcoded
    combination."""
    if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
        return 0
    try:
        df = pd.read_csv(output_file, low_memory=False)
        count = ((df["Type"] == diamond_type) & (df["ShapeName"] == shape_name)).sum()
    except Exception as e:
        print(f"Could not determine resume point from {output_file}: {e}")
        return 0
    return int(count // per_page)


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def scrape_shape(url, shape_id, filters, result_key, diamond_type, shape_name,
                  output_file, seen_ids):
    """Fetch page by page and write each page's rows to output_file as
    soon as they arrive. Resumes from the last saved page for this
    specific shape + diamond type.

    Stops when either:
      - the API returns a genuinely empty batch, or
      - MAX_CONSECUTIVE_DUPE_PAGES pages in a row come back with 0 new
        rows (all diamonds already seen) - this catches backends that
        clamp/loop pagination instead of returning an empty list.
    """

    pager = get_start_pager(output_file, diamond_type, shape_name)
    total_written = 0
    consecutive_all_dupe_pages = 0

    if pager > 0:
        print(f"Resuming {diamond_type}/{shape_name} at page {pager}")

    while True:
        batch = fetch_batch(url, shape_id, pager, filters, result_key)

        if not batch:
            print("No more diamonds for this shape (empty response)")
            break

        rows = []
        for d in batch:
            row = row_from_diamond(d)
            row["Type"] = diamond_type
            row["ShapeName"] = shape_name

            diamond_id = str(row["ID"])
            if diamond_id in seen_ids:
                continue
            seen_ids.add(diamond_id)
            rows.append(row)

        write_rows_to_csv(rows, output_file)

        total_written += len(rows)
        print(f"Page {pager}: {len(rows)} new rows written "
              f"(total so far for this shape: {total_written})")

        if len(rows) == 0:
            consecutive_all_dupe_pages += 1
            print(f"  (page was 100% duplicates - "
                  f"{consecutive_all_dupe_pages}/{MAX_CONSECUTIVE_DUPE_PAGES} consecutive)")
            if consecutive_all_dupe_pages >= MAX_CONSECUTIVE_DUPE_PAGES:
                print(f"Stopping {shape_name}: API is repeating already-seen "
                      f"data, treating as end of results.")
                break
        else:
            consecutive_all_dupe_pages = 0  # reset on real progress

        pager += 1
        time.sleep(random.uniform(0.8, 1.8))

    return total_written


def scrape_diamonds(diamond_type, output_file, shapes=None):
    """
    diamond_type: "lab" or "natural"
    output_file: CSV path to write to (rows are appended page by page)
    shapes: list of shape names from SHAPES, defaults to all shapes
    """
    if diamond_type == "lab":
        url = LAB_URL
        filters = LAB_FILTERS
        result_key = "diamond"
    elif diamond_type == "natural":
        url = NATURAL_URL
        filters = NATURAL_FILTERS
        result_key = "diamond"
    else:
        raise ValueError("diamond_type must be 'lab' or 'natural'")

    shapes = shapes or list(SHAPES.keys())

    ensure_header(output_file)
    seen_ids = load_existing_ids(output_file)
    print(f"Resuming with {len(seen_ids)} IDs already in {output_file}")

    grand_total = 0
    for shape in shapes:
        print(f"\n=== {diamond_type.upper()} - {shape} ===")
        shape_id = SHAPES[shape]
        written = scrape_shape(
            url, shape_id, filters, result_key,
            diamond_type, shape, output_file, seen_ids,
        )
        grand_total += written

    return grand_total


if __name__ == "__main__":

    LAB_CSV = "diamonds_lab.csv"
    NATURAL_CSV = "diamonds_natural.csv"
    ALL_CSV = "diamonds_all.csv"

    lab_total = scrape_diamonds("lab", LAB_CSV)
    print(f"\nSaved {lab_total} new lab-grown diamonds -> {LAB_CSV}")

    natural_total = scrape_diamonds("natural", NATURAL_CSV)
    print(f"Saved {natural_total} new natural diamonds -> {NATURAL_CSV}")

    # Combine both files into diamonds_all.csv at the end.
    frames = []
    if os.path.exists(LAB_CSV):
        frames.append(pd.read_csv(LAB_CSV, low_memory=False))
    if os.path.exists(NATURAL_CSV):
        frames.append(pd.read_csv(NATURAL_CSV, low_memory=False))

    if frames:
        all_df = pd.concat(frames, ignore_index=True)
        all_df = all_df.drop_duplicates(subset=["ID"])
        all_df.to_csv(ALL_CSV, index=False)
        print(f"Saved {len(all_df)} total diamonds -> {ALL_CSV}")
        #  all_df = pd.concat(frames, ignore_index=True)
                # all_df = all_df.drop_duplicates(subset=["ID"])
                
        