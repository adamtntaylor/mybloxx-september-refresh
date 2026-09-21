#!/usr/bin/env python3
import datetime
import pathlib
import re
import urllib.request

SOURCES = [
    # Compact, actively maintained mobile/browser-oriented base.
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/ultimate.mini-onlydomains.txt",
    # Mullvad's own current custom ad/tracker additions.
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/files/adblock",
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/files/tracker",
]

# High-confidence ad hosts that must remain covered even if an upstream list changes.
REQUIRED_BLOCK_DOMAINS = {
    "doubleclick.net",
    "googlesyndication.com",
    "googleadservices.com",
    "adservice.google.com",
    "2mdn.net",
}

MIN_BLOCKED_DOMAINS = 10000
DOMAIN = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9_-]{0,62}[a-z0-9])?\.)+[a-z0-9][a-z0-9_-]{0,62}$",
    re.I,
)

def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MYbloXX-September-Refresh/2.0",
            "Cache-Control": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read().decode("utf-8", "replace")
    if not data.strip():
        raise RuntimeError(f"Source returned empty content: {url}")
    return data

def parse(text):
    out = set()
    for raw in text.splitlines():
        s = raw.strip().lower()
        if not s or s.startswith(("#", "!", ";")):
            continue

        # Adblock-style hostname rule.
        if s.startswith("||"):
            s = s[2:]
            s = s.split("^", 1)[0].split("$", 1)[0]

        # Hosts-file style rule.
        parts = s.split()
        if len(parts) >= 2 and parts[0] in ("0.0.0.0", "127.0.0.1", "::1"):
            s = parts[1]

        if s.startswith("*."):
            s = s[2:]

        # Ignore URL/path/regex rules; PAC host matching is domain-based.
        if "*" in s or "/" in s or ":" in s:
            continue

        s = s.split("^", 1)[0].split("$", 1)[0].strip(".")
        if DOMAIN.fullmatch(s):
            out.add(s)
    return out

def minimize(domains):
    # If a parent is blocked, its subdomains do not need separate entries.
    kept = set()
    for d in sorted(domains, key=lambda x: (x.count("."), x)):
        parts = d.split(".")
        has_parent = any(
            ".".join(parts[i:]) in kept
            for i in range(1, len(parts) - 1)
        )
        if not has_parent:
            kept.add(d)
    return sorted(kept)

def covered(domain, domains):
    domain = domain.lower().strip(".")
    if domain in domains:
        return True
    parts = domain.split(".")
    return any(".".join(parts[i:]) in domains for i in range(1, len(parts) - 1))

allow_path = pathlib.Path("allowlist.txt")
allow = parse(allow_path.read_text(encoding="utf-8")) if allow_path.exists() else set()

domains = set()
source_counts = {}
for url in SOURCES:
    parsed = parse(fetch(url))
    source_counts[url] = len(parsed)
    domains |= parsed

domains |= REQUIRED_BLOCK_DOMAINS
domains -= allow
domains = set(minimize(domains))

# Hard fail instead of ever publishing an empty/useless PAC.
if len(domains) < MIN_BLOCKED_DOMAINS:
    raise RuntimeError(
        f"Refusing to publish: only {len(domains):,} blocked domains were generated "
        f"(minimum {MIN_BLOCKED_DOMAINS:,}). Source counts: {source_counts}"
    )

if not covered("g.doubleclick.net", domains):
    raise RuntimeError("Refusing to publish: g.doubleclick.net is not covered.")

if "shop.tiktok.com" not in allow:
    raise RuntimeError("Refusing to publish: shop.tiktok.com is missing from allowlist.")

block = "{" + ",".join(repr(d) + ":1" for d in sorted(domains)) + "}"
allowed = "{" + ",".join(repr(d) + ":1" for d in sorted(allow)) + "}"
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

pac = f"""// MYbloXX September Refresh 2026 — validated mobile PAC
// Generated: {stamp}
// Sources: HaGeZi Ultimate mini + Mullvad custom adblock/tracker lists.
// Explicit exception: shop.tiktok.com
// Blocked domains after parent-domain minimization: {len(domains)}
var BLOCK={block};
var ALLOW={allowed};
var BLOCKED="PROXY 127.0.0.1:8021";
var DIRECT="DIRECT";

function suffixMatch(t,h){{
  if(t[h]) return true;
  var p=h.indexOf(".");
  while(p>0){{
    h=h.substring(p+1);
    if(t[h]) return true;
    p=h.indexOf(".");
  }}
  return false;
}}

function localHost(h){{
  if(!h || isPlainHostName(h)) return true;
  if(h=="localhost" || dnsDomainIs(h,".local") || dnsDomainIs(h,".lan") || dnsDomainIs(h,".home.arpa")) return true;
  if(/^127\./.test(h) || /^10\./.test(h) || /^192\.168\./.test(h)) return true;
  var m=/^172\.(\d+)\./.exec(h);
  return !!(m && Number(m[1])>=16 && Number(m[1])<=31);
}}

function FindProxyForURL(url,host){{
  host=(host||"").toLowerCase().replace(/\.$/,"");
  if(localHost(host)) return DIRECT;
  if(suffixMatch(ALLOW,host)) return DIRECT;
  if(suffixMatch(BLOCK,host)) return BLOCKED;
  return DIRECT;
}}
"""

pathlib.Path("mybloxx-september-refresh.pac").write_text(pac, encoding="utf-8")

print(f"Wrote {len(domains):,} blocked domains.")
for url, count in source_counts.items():
    print(f"  {count:,} parsed from {url}")
print(f"Allowlist: {', '.join(sorted(allow))}")
print("Verified: g.doubleclick.net is BLOCKED; shop.tiktok.com is DIRECT.")
