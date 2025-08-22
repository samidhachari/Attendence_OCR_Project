# import re
# from datetime import datetime
# from typing import List, Dict

# TIME_RE = re.compile(r"([01]?\d|2[0-3])[:\.]([0-5]\d)(?:\s*(AM|PM|am|pm))?")
# DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")

# def normalize_date(s: str) -> str:
#     s = s.strip().replace("/", "-")
#     # try common patterns
#     for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y"):
#         try:
#             dt = datetime.strptime(s, fmt)
#             return dt.strftime("%Y-%m-%d")
#         except Exception:
#             continue
#     # fallback: if format dd-mm-yy
#     parts = s.split("-")
#     if len(parts) == 3:
#         dd, mm, yy = parts
#         try:
#             if len(yy) == 2:
#                 year = 2000 + int(yy)
#             else:
#                 year = int(yy)
#             return f"{year:04d}-{int(mm):02d}-{int(dd):02d}"
#         except Exception:
#             pass
#     return s

# def normalize_time(s: str) -> str:
#     if not s:
#         return ""
#     s = s.strip().replace(".", ":")
#     m = TIME_RE.search(s)
#     if not m:
#         return s
#     hh, mm, ap = m.groups()
#     hh = int(hh)
#     mm = int(mm)
#     if ap:
#         ap = ap.lower()
#         if ap == "pm" and hh != 12:
#             hh += 12
#         if ap == "am" and hh == 12:
#             hh = 0
#     return f"{hh:02d}:{mm:02d}"

# def parse_text(text: str) -> List[Dict]:
#     """
#     Robust parse: iterate lines, skip headers, split on '|' if present, detect date and times,
#     avoid duplicate entries.
#     """
#     rows = []
#     seen = set()

#     # Normalize and split lines
#     raw_lines = [l.strip().strip(",") for l in text.splitlines() if l.strip()]
#     # collapse multi-space sequences
#     norm_lines = [re.sub(r"\s{2,}", " | ", l) for l in raw_lines]

#     for line in norm_lines:
#         # skip header-like lines
#         if re.search(r"\b(date|staff|name|check in|check out|table)\b", line, flags=re.I):
#             continue

#         # If pipe present, try splitting to components
#         if "|" in line:
#             parts = [p.strip() for p in line.split("|") if p.strip()]
#             # Common patterns:
#             # [date] | [name] | [in] | [out]
#             # [date] | [name [in] [out]]  (in/out appended)
#             if len(parts) >= 4:
#                 date_raw = parts[0]
#                 name = parts[1]
#                 ci = parts[2]
#                 co = parts[3]
#                 d = normalize_date(date_raw)
#                 ci = normalize_time(ci)
#                 co = normalize_time(co)
#                 key = (d, name, ci, co)
#                 if key not in seen:
#                     rows.append({"date": d, "name": name, "check_in": ci, "check_out": co})
#                     seen.add(key)
#                 continue
#             elif len(parts) == 3:
#                 date_raw = parts[0]
#                 tail = parts[1] + " " + parts[2]
#                 # try to locate times at tail end
#                 times = re.findall(r"\d{1,2}[:.]\d{2}", tail)
#                 if len(times) >= 2:
#                     name = re.sub(r"\d{1,2}[:.]\d{2}.*$", "", tail).strip()
#                     d = normalize_date(date_raw)
#                     ci = normalize_time(times[0])
#                     co = normalize_time(times[1])
#                     key = (d, name, ci, co)
#                     if key not in seen:
#                         rows.append({"date": d, "name": name, "check_in": ci, "check_out": co})
#                         seen.add(key)
#                     continue

#         # fallback: token approach
#         tokens = re.split(r"\s+", line)
#         time_idxs = [i for i, t in enumerate(tokens) if re.search(r"\d{1,2}[:.]\d{2}", t)]
#         date_match = DATE_RE.search(line)
#         if date_match and len(time_idxs) >= 2:
#             date_raw = date_match.group(0)
#             # assume date token is the first token containing date
#             # find first time index
#             first_time_idx = time_idxs[0]
#             second_time_idx = time_idxs[1]
#             name_tokens = tokens[:first_time_idx]
#             # remove date from name_tokens if present
#             if date_raw in name_tokens:
#                 name_tokens = [t for t in name_tokens if t != date_raw]
#             name = " ".join(name_tokens).strip()
#             d = normalize_date(date_raw)
#             ci = normalize_time(tokens[first_time_idx])
#             co = normalize_time(tokens[second_time_idx])
#             key = (d, name, ci, co)
#             if key not in seen:
#                 rows.append({"date": d, "name": name, "check_in": ci, "check_out": co})
#                 seen.add(key)
#             continue

#         # If line contains multiple date patterns (concatenated rows), split by date
#         date_positions = list(re.finditer(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", line))
#         if len(date_positions) > 1:
#             # naive split by date occurrences and parse each sub-chunk
#             chunks = re.split(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", line)
#             # chunks like ["", "01-08-25", " name 8:00 17:00 ", "02-08-25", " name2 9:00 17:00"]
#             for i in range(1, len(chunks), 2):
#                 date_raw = chunks[i]
#                 content = chunks[i+1] if i+1 < len(chunks) else ""
#                 sub_tokens = re.split(r"\s+", content.strip())
#                 t_idxs = [j for j, t in enumerate(sub_tokens) if re.search(r"\d{1,2}[:.]\d{2}", t)]
#                 if len(t_idxs) >= 2:
#                     ci = normalize_time(sub_tokens[t_idxs[0]])
#                     co = normalize_time(sub_tokens[t_idxs[1]])
#                     name = " ".join(sub_tokens[:t_idxs[0]]).strip()
#                     d = normalize_date(date_raw)
#                     key = (d, name, ci, co)
#                     if key not in seen:
#                         rows.append({"date": d, "name": name, "check_in": ci, "check_out": co})
#                         seen.add(key)
#             continue

#     return row



import re
from datetime import datetime
from typing import List, Dict

TIME_RE = re.compile(r"([01]?\d|2[0-3])[:\.]([0-5]\d)(?:\s*(AM|PM|am|pm))?")
DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")

def normalize_date(s: str) -> str:
    s = s.strip().replace("/", "-")
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    parts = s.split("-")
    if len(parts) == 3:
        dd, mm, yy = parts
        try:
            if len(yy) == 2:
                year = 2000 + int(yy)
            else:
                year = int(yy)
            return f"{year:04d}-{int(mm):02d}-{int(dd):02d}"
        except Exception:
            pass
    return s

def normalize_time(s: str) -> str:
    if not s:
        return ""
    s = s.strip().replace(".", ":")
    m = TIME_RE.search(s)
    if not m:
        return s
    hh, mm, ap = m.groups()
    hh = int(hh)
    mm = int(mm)
    if ap:
        ap = ap.lower()
        if ap == "pm" and hh != 12:
            hh += 12
        if ap == "am" and hh == 12:
            hh = 0
    return f"{hh:02d}:{mm:02d}"

def parse_text(text: str) -> List[Dict]:
    rows = []
    seen = set()

    raw_lines = [l.strip().strip(",") for l in text.splitlines() if l.strip()]
    norm_lines = [re.sub(r"\s{2,}", " | ", l) for l in raw_lines]

    for line in norm_lines:
        if re.search(r"\b(date|staff|name|check in|check out|table)\b", line, flags=re.I):
            continue

        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                date_raw, name, ci, co = parts[0], parts[1], parts[2], parts[3]
                d = normalize_date(date_raw)
                ci = normalize_time(ci)
                co = normalize_time(co)
                key = (d, name, ci, co)
                if key not in seen:
                    rows.append({"date": d, "name": name, "check_in": ci, "check_out": co})
                    seen.add(key)
                continue
            elif len(parts) == 3:
                date_raw = parts[0]
                tail = parts[1] + " " + parts[2]
                times = re.findall(r"\d{1,2}[:.]\d{2}", tail)
                if len(times) >= 2:
                    name = re.sub(r"\d{1,2}[:.]\d{2}.*$", "", tail).strip()
                    d = normalize_date(date_raw)
                    ci = normalize_time(times[0])
                    co = normalize_time(times[1])
                    key = (d, name, ci, co)
                    if key not in seen:
                        rows.append({"date": d, "name": name, "check_in": ci, "check_out": co})
                        seen.add(key)
                    continue

        tokens = re.split(r"\s+", line)
        time_idxs = [i for i, t in enumerate(tokens) if re.search(r"\d{1,2}[:.]\d{2}", t)]
        date_match = DATE_RE.search(line)
        if date_match and len(time_idxs) >= 2:
            date_raw = date_match.group(0)
            first_time_idx = time_idxs[0]
            second_time_idx = time_idxs[1]
            name_tokens = tokens[:first_time_idx]
            if date_raw in name_tokens:
                name_tokens = [t for t in name_tokens if t != date_raw]
            name = " ".join(name_tokens).strip()
            d = normalize_date(date_raw)
            ci = normalize_time(tokens[first_time_idx])
            co = normalize_time(tokens[second_time_idx])
            key = (d, name, ci, co)
            if key not in seen:
                rows.append({"date": d, "name": name, "check_in": ci, "check_out": co})
                seen.add(key)
            continue

        date_positions = list(re.finditer(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", line))
        if len(date_positions) > 1:
            chunks = re.split(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", line)
            for i in range(1, len(chunks), 2):
                date_raw = chunks[i]
                content = chunks[i+1] if i+1 < len(chunks) else ""
                sub_tokens = re.split(r"\s+", content.strip())
                t_idxs = [j for j, t in enumerate(sub_tokens) if re.search(r"\d{1,2}[:.]\d{2}", t)]
                if len(t_idxs) >= 2:
                    ci = normalize_time(sub_tokens[t_idxs[0]])
                    co = normalize_time(sub_tokens[t_idxs[1]])
                    name = " ".join(sub_tokens[:t_idxs[0]]).strip()
                    d = normalize_date(date_raw)
                    key = (d, name, ci, co)
                    if key not in seen:
                        rows.append({"date": d, "name": name, "check_in": ci, "check_out": co})
                        seen.add(key)

    return rows



