



# import re
# from datetime import datetime
# from typing import List, Dict

# TIME_RE = re.compile(r"([01]?\d|2[0-3])[:\.]([0-5]\d)(?:\s*(AM|PM|am|pm))?")
# DATE_RE = re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")

# def normalize_date(s: str) -> str:
#     s = s.strip().replace("/", "-")
#     for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y"):
#         try:
#             dt = datetime.strptime(s, fmt)
#             return dt.strftime("%Y-%m-%d")
#         except Exception:
#             continue
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
#     rows = []
#     seen = set()

#     raw_lines = [l.strip().strip(",") for l in text.splitlines() if l.strip()]
#     norm_lines = [re.sub(r"\s{2,}", " | ", l) for l in raw_lines]

#     for line in norm_lines:
#         if re.search(r"\b(date|staff|name|check in|check out|table)\b", line, flags=re.I):
#             continue

#         if "|" in line:
#             parts = [p.strip() for p in line.split("|") if p.strip()]
#             if len(parts) >= 4:
#                 date_raw, name, ci, co = parts[0], parts[1], parts[2], parts[3]
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

#         tokens = re.split(r"\s+", line)
#         time_idxs = [i for i, t in enumerate(tokens) if re.search(r"\d{1,2}[:.]\d{2}", t)]
#         date_match = DATE_RE.search(line)
#         if date_match and len(time_idxs) >= 2:
#             date_raw = date_match.group(0)
#             first_time_idx = time_idxs[0]
#             second_time_idx = time_idxs[1]
#             name_tokens = tokens[:first_time_idx]
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

#         date_positions = list(re.finditer(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", line))
#         if len(date_positions) > 1:
#             chunks = re.split(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", line)
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

#     return rows


import re
from datetime import datetime
from typing import List, Dict, Tuple

TIME_RE = re.compile(r"([01]?\d|2[0-3])[:\.]([0-5]\d)(?:\s*(AM|PM|am|pm))?")
DATE_RE = re.compile(r"\b(\d{1,2}[-/]\s?\d{1,2}[-/]\s?\d{2,4}|\d{4}[-/]\d{2}[-/]\d{2})\b")

def normalize_date(s: str) -> str:
    """Normalize various date formats to YYYY-MM-DD"""
    if not s:
        return ""
    
    # Clean up the date string
    s = s.strip().replace("/", "-").replace(" ", "")
    
    # Try different date formats
    formats = [
        "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", 
        "%d-%m-%y", "%m-%d-%y", "%y-%m-%d"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # If all else fails, return the original (cleaned)
    return s

def normalize_time(s: str) -> str:
    """Normalize various time formats to HH:MM"""
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
        elif ap == "am" and hh == 12:
            hh = 0
    
    # Handle 12-hour format without AM/PM (common in your images)
    if not ap and hh < 8:  # Assume times like "7:00" are PM in work context
        hh += 12
    
    return f"{hh:02d}:{mm:02d}"

def extract_table_data(line: str) -> Tuple[str, str, str, str]:
    """Extract date, name, check_in, check_out from various line formats"""
    
    # Format 1: Pipe-separated values (like data.jpg)
    if "|" in line and line.count("|") >= 3:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 4:
            return parts[0], parts[1], parts[2], parts[3]
    
    # Format 2: Space-separated date components (like image1.jpeg)
    date_match = DATE_RE.search(line)
    if date_match:
        date_raw = date_match.group(0)
        
        # Remove date from line to extract name and times
        remaining = DATE_RE.sub("", line).strip()
        
        # Find all times in remaining text
        times = []
        for time_match in TIME_RE.finditer(remaining):
            times.append(time_match.group(0))
        
        # Name is everything except times
        name_text = TIME_RE.sub("", remaining).strip()
        
        if len(times) >= 2:
            return date_raw, name_text, times[0], times[1]
        elif len(times) == 1:
            return date_raw, name_text, times[0], ""
    
    # Format 3: Try to split by multiple spaces (tab-like)
    tokens = re.split(r"\s{2,}", line)
    if len(tokens) >= 4:
        return tokens[0], tokens[1], tokens[2], tokens[3]
    
    return "", "", "", ""

def parse_text(text: str) -> List[Dict]:
    """Parse OCR text into structured attendance data"""
    rows = []
    seen = set()
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    for line in lines:
        # Skip header lines
        if re.search(r"\b(date|staff|name|check|time|table)\b", line, re.I):
            continue
        
        # Extract data from the line
        date_raw, name, check_in, check_out = extract_table_data(line)
        
        # Skip if no meaningful data found
        if not date_raw and not name:
            continue
        
        # Normalize the extracted data
        normalized_date = normalize_date(date_raw)
        normalized_check_in = normalize_time(check_in)
        normalized_check_out = normalize_time(check_out)
        
        # Clean up name (remove extra punctuation, etc.)
        name = re.sub(r"[^\w\s]", "", name).strip()
        
        # Create unique key to avoid duplicates
        key = (normalized_date, name, normalized_check_in, normalized_check_out)
        if key not in seen:
            rows.append({
                "date": normalized_date,
                "name": name,
                "check_in": normalized_check_in,
                "check_out": normalized_check_out
            })
            seen.add(key)
    
    return rows


