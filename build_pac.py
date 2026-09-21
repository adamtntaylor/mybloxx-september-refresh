#!/usr/bin/env python3
import datetime
import pathlib
import re
import urllib.request

SOURCES = [
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/light-onlydomains.txt",
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/files/adblock",
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/files/tracker",
]

REQUIRED_BLOCK_DOMAINS = {
    "doubleclick.net",
    "googlesyndication.com",
    "googleadservices.com",
    "googletagservices.com",
    "adservice.google.com",
    "2mdn.net",
}

TOKEN = re.compile(
    r'(^|[.\-_])'
    r'(ad(?:s|server|service|system|network|tech|exchange|form|roll|mob|nxs|colony|cash|push|click|vert|ver|v)?'
    r'|track(?:er|ing)?|analytics?|telemetry|metrics?|pixel|beacon|sponsor|promo|affiliate|affiliat'
    r'|impression|rtb|ssp|dsp|bid|criteo|taboola|outbrain|doubleclick|googlesyndication'
    r'|googleadservices|appsflyer|adjust|branch|amplitude|mixpanel|segment)'
    r'([.\-_]|$)',
    re.I,
)

DOMAIN = re.compile(r'^(?:[a-z0-9](?:[a-z0-9_-]{0,62}[a-z0-9])?\.)+[a-z0-9][a-z0-9_-]{0,62}$', re.I)
MIN_FRESH = 2500
MAX_PAC_BYTES = 300000

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "MYbloXX-September-Refresh-Compact/1.0",
        "Cache-Control": "no-cache",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read().decode("utf-8", "replace")
    if not data.strip():
        raise RuntimeError(f"Empty source: {url}")
    return data

def normalize(raw):
    s = raw.strip().lower()
    if not s or s.startswith(("#", "!", ";")):
        return None
    if s.startswith("||"):
        s = s[2:].split("^", 1)[0].split("$", 1)[0]
    parts = s.split()
    if len(parts) >= 2 and parts[0] in ("0.0.0.0", "127.0.0.1", "::1"):
        s = parts[1]
    if s.startswith("*."):
        s = s[2:]
    if "*" in s or "/" in s or ":" in s:
        return None
    s = s.strip(".")
    return s if DOMAIN.fullmatch(s) else None

def parse_all(text):
    out = set()
    for raw in text.splitlines():
        d = normalize(raw)
        if d:
            out.add(d)
    return out

def parse_allowlist(path):
    if not path.exists():
        return set()
    return parse_all(path.read_text(encoding="utf-8"))

legacy_path = pathlib.Path("legacy-mybloxx-base.pac")
if not legacy_path.exists():
    raise RuntimeError("Missing legacy-mybloxx-base.pac")

legacy = legacy_path.read_text(encoding="utf-8")
allow = parse_allowlist(pathlib.Path("allowlist.txt"))

hagezi = parse_all(fetch(SOURCES[0]))
fresh = {d for d in hagezi if TOKEN.search(d)}

for url in SOURCES[1:]:
    fresh |= parse_all(fetch(url))

fresh |= REQUIRED_BLOCK_DOMAINS
fresh -= allow

if len(fresh) < MIN_FRESH:
    raise RuntimeError(f"Refusing to publish: only {len(fresh):,} fresh domains selected.")

fresh_obj = "var FRESH={" + ",".join(repr(d)+":1" for d in sorted(fresh)) + "};"
helper = (
    "function freshMatch(h){if(FRESH[h])return true;var p=h.indexOf(\".\");"
    "while(p>0){h=h.substring(p+1);if(FRESH[h])return true;p=h.indexOf(\".\");}return false;}"
)

marker = 'var MYbloXX="PROXY 127.0.0.1:8021";var ALLOW="DIRECT";var BYPASS="PROXY 8.8.8.8:53";'
replacement = (
    'var MYbloXX="PROXY 127.0.0.1:8021";var ALLOW="DIRECT";'
    'var BYPASS="PROXY 127.0.0.1:8021";' + fresh_obj + helper
)

if marker not in legacy:
    raise RuntimeError("Legacy PAC marker not found.")
pac = legacy.replace(marker, replacement, 1)

anchor = 'function FindProxyForURL(url,host){var u=url.toLowerCase();var h=host.toLowerCase();'
if anchor not in pac:
    raise RuntimeError("Legacy FindProxyForURL anchor not found.")

allow_checks = []
for d in sorted(allow):
    allow_checks.append(f'h=="{d}"||dnsDomainIs(h,".{d}")')
allow_expr = "||".join(allow_checks) or "false"

stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
inject = (
    anchor
    + f'if({allow_expr})return ALLOW;'
    + 'if(freshMatch(h))return MYbloXX;'
)
pac = pac.replace(anchor, inject, 1)

header = (
    "//\n"
    "// MYbloXX September Refresh 2026 — Compact\n"
    f"// Generated: {stamp}\n"
    f"// Current compact additions: {len(fresh):,} domains from HaGeZi LIGHT + Mullvad custom rules.\n"
    "// Explicit allowlist is evaluated before every block rule.\n"
    "//\n"
)
# Replace only the opening legacy comment block.
pac = re.sub(
    r'^//\n// MYbloXX by MYXXdev \(Default\)\n// Updated:[^\n]*\n// Support Development:[^\n]*\n//',
    header,
    pac,
    count=1,
)

size = len(pac.encode("utf-8"))
if size > MAX_PAC_BYTES:
    raise RuntimeError(f"Refusing to publish: compact PAC grew to {size:,} bytes.")
if "doubleclick.net" not in pac:
    raise RuntimeError("Refusing to publish: doubleclick.net missing.")
if "shop.tiktok.com" not in pac:
    raise RuntimeError("Refusing to publish: shop.tiktok.com allowlist missing.")

pathlib.Path("mybloxx-september-refresh.pac").write_text(pac, encoding="utf-8")
print(f"Wrote compact PAC: {size:,} bytes, {len(fresh):,} current domains.")
print("Verified: DoubleClick covered; shop.tiktok.com explicitly allowed.")
