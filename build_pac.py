#!/usr/bin/env python3
import pathlib,re,urllib.request

SOURCES = [
    "https://raw.githubusercontent.com/sjhgvr/oisd/main/domainswild2_small.txt",
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/files/adblock",
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/files/tracker",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt",
]
DOMAIN = re.compile(r"^(?:[a-z0-9](?:[a-z0-9_-]{0,62}[a-z0-9])?\\.)+[a-z0-9][a-z0-9_-]{0,62}$", re.I)

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"MYbloXX-September-Refresh/1.0","Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read().decode("utf-8","replace")

def parse(text):
    out=set()
    for raw in text.splitlines():
        s=raw.strip().lower()
        if not s or s.startswith(("#","!",";")): continue
        if s.startswith("||"):
            s=s[2:].split("^",1)[0].split("$",1)[0]
        parts=s.split()
        if len(parts)>=2 and parts[0] in ("0.0.0.0","127.0.0.1","::1"):
            s=parts[1]
        if s.startswith("*."): s=s[2:]
        if "*" in s or "/" in s or ":" in s: continue
        s=s.split("^",1)[0].split("$",1)[0].strip(".")
        if DOMAIN.match(s): out.add(s)
    return out

def minimize(domains):
    kept=set()
    for d in sorted(domains,key=lambda x:(x.count("."),x)):
        parts=d.split(".")
        if not any(".".join(parts[i:]) in kept for i in range(1,len(parts)-1)):
            kept.add(d)
    return sorted(kept)

allow=set(parse(pathlib.Path("allowlist.txt").read_text())) if pathlib.Path("allowlist.txt").exists() else set()
domains=set()
for url in SOURCES:
    domains |= parse(fetch(url))
domains -= allow
domains=minimize(domains)

block="{" + ",".join(repr(d)+":1" for d in domains) + "}"
allowed="{" + ",".join(repr(d)+":1" for d in sorted(allow)) + "}"
pac="""// MYbloXX September Refresh 2026 — Mullvad Mobile PAC
// Auto-generated from OISD Small, Mullvad custom ads/trackers, and AdGuard Mobile.
// Aggressive TikTok-specific tracker lists are intentionally excluded.
var BLOCK=%s;
var ALLOW=%s;
var BLOCKED="PROXY 127.0.0.1:8021";
var DIRECT="DIRECT";
function suffixMatch(t,h){if(t[h])return true;var p=h.indexOf(".");while(p>0){h=h.substring(p+1);if(t[h])return true;p=h.indexOf(".");}return false;}
function localHost(h){if(!h||isPlainHostName(h))return true;if(h=="localhost"||dnsDomainIs(h,".local")||dnsDomainIs(h,".lan")||dnsDomainIs(h,".home.arpa"))return true;if(/^127\\./.test(h)||/^10\\./.test(h)||/^192\\.168\\./.test(h))return true;var m=/^172\\.(\\d+)\\./.exec(h);return !!(m&&Number(m[1])>=16&&Number(m[1])<=31);}
function FindProxyForURL(url,host){host=(host||"").toLowerCase().replace(/\\.$/,"");if(localHost(host))return DIRECT;if(suffixMatch(ALLOW,host))return DIRECT;if(suffixMatch(BLOCK,host))return BLOCKED;return DIRECT;}
""" % (block,allowed)
pathlib.Path("mybloxx-september-refresh.pac").write_text(pac,encoding="utf-8")
print(f"Wrote {len(domains):,} blocked domains; allowlist: {', '.join(sorted(allow)) or '(none)'}")
