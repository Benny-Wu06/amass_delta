import json
import logging
import re
import time
import urllib.request
import urllib.parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MAX_ITEMS = 30
NVD_DELAY = 0.25


def calculate_risk(cvss, epss):
    if cvss is None or epss is None:
        return 0.0, "UNKNOWN"
    risk_index = round((float(cvss) / 10) * 0.6 + float(epss) * 0.4, 4)
    if risk_index >= 0.8:
        return risk_index, "CRITICAL"
    if risk_index >= 0.6:
        return risk_index, "HIGH"
    if risk_index >= 0.4:
        return risk_index, "MEDIUM"
    return risk_index, "LOW"


def parse_version(v):
    """Convert a version string like '2.53.0' into a comparable int tuple."""
    if not v:
        return ()
    result = []
    for part in re.split(r'[.\-_]', str(v)):
        m = re.match(r'^(\d+)', part)
        if m:
            result.append(int(m.group(1)))
        else:
            break
    return tuple(result)


def is_version_affected(installed_version, configurations):
    """
    Returns True if installed_version falls within any vulnerable CPE range.
    Falls back to True (assume vulnerable) when version info is missing.
    """
    if not installed_version or installed_version.lower() == 'unknown':
        return True

    iv = parse_version(installed_version)
    if not iv:
        return True

    cpe_matches = [
        match
        for config in configurations
        for node in config.get('nodes', [])
        for match in node.get('cpeMatch', [])
        if match.get('vulnerable', True)
    ]

    if not cpe_matches:
        return True

    has_any_range = False

    for match in cpe_matches:
        si = match.get('versionStartIncluding')
        se = match.get('versionStartExcluding')
        ei = match.get('versionEndIncluding')
        ee = match.get('versionEndExcluding')

        if not any([si, se, ei, ee]):
            return True  # no version constraint = all versions affected

        has_any_range = True

        # Check lower bound
        if si and iv < parse_version(si):
            continue
        if se and iv <= parse_version(se):
            continue
        # Check upper bound
        if ei and iv > parse_version(ei):
            continue
        if ee and iv >= parse_version(ee):
            continue

        return True  # installed version is within this vulnerable range

    # Had version ranges but none matched → not affected
    return not has_any_range


def query_nvd(keyword):
    encoded = urllib.parse.quote(keyword)
    url = f"{NVD_API}?keywordSearch={encoded}&resultsPerPage=5"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "amass-delta-scanner/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        time.sleep(NVD_DELAY)
        return data.get("vulnerabilities", [])
    except Exception as exc:
        logger.warning("NVD query failed for '%s': %s", keyword, exc)
        return []


def extract_cve_entry(nvd_item, software_label, installed_version):
    cve = nvd_item.get("cve", {})
    cve_id = cve.get("id", "")

    if not is_version_affected(installed_version, cve.get("configurations", [])):
        return None

    descriptions = cve.get("descriptions", [])
    description = next((d["value"] for d in descriptions if d.get("lang") == "en"), "No description available.")

    cvss_score = None
    metrics = cve.get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        entries = metrics.get(key, [])
        if entries:
            try:
                cvss_score = float(entries[0]["cvssData"]["baseScore"])
            except (KeyError, TypeError, ValueError):
                pass
            break

    epss_score = 0.0
    risk_index, risk_rating = calculate_risk(cvss_score or 0.0, epss_score)

    published = cve.get("published", "")[:10]

    return {
        "cve_id": cve_id,
        "vulnerability_name": cve.get("vulnStatus", ""),
        "description": description[:400],
        "cvss_score": cvss_score,
        "epss_score": epss_score,
        "risk_index": risk_index,
        "risk_rating": risk_rating,
        "affected_software": software_label,
        "published": published,
    }


def lambda_handler(event, context):
    try:
        raw_body = event.get("body", "{}")
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON body"})

    software_list = body.get("software", [])
    os_info       = body.get("os", {})
    scanned_at    = body.get("scanned_at", "")

    seen, unique_items = set(), []
    for item in software_list:
        name = item.get("name", "").strip()
        if name and name not in seen:
            seen.add(name)
            unique_items.append(item)
    unique_items = unique_items[:MAX_ITEMS]

    logger.info("Scanning %d software items", len(unique_items))

    matched: dict = {}
    for item in unique_items:
        name    = item.get("name", "")
        version = item.get("version", "")
        label   = f"{name} {version}".strip()

        for nvd_item in query_nvd(name):
            entry = extract_cve_entry(nvd_item, label, version)
            if not entry or not entry["cve_id"]:
                continue
            cve_id = entry["cve_id"]
            if cve_id not in matched or entry["risk_index"] > matched[cve_id]["risk_index"]:
                matched[cve_id] = entry

    result_list = sorted(matched.values(), key=lambda x: x["risk_index"], reverse=True)

    return _response(200, {
        "matched_cves":          result_list,
        "software_scanned":      len(unique_items),
        "vulnerabilities_found": len(result_list),
        "os":                    os_info,
        "scanned_at":            scanned_at,
    })


def _response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(payload),
    }
