# MYbloXX iOS Refresh

Current recommended build: **October 2026 — Systemwide Hybrid**

This project now combines the two approaches that worked best during testing:

1. a compact supervised **Global HTTP Proxy / PAC** for broad HTTP/HTTPS filtering across Wi-Fi and cellular
2. **Control D + HaGeZi Pro DNS** as a secondary filtering layer wherever iOS is using the system DNS path

## Recommended profile

Install:

`MYbloXX-October-2026-Systemwide-Hybrid.mobileconfig`

It contains:

- `com.apple.proxy.http.global`
- PAC URL: `https://raw.githubusercontent.com/adamtntaylor/mybloxx-september-refresh/main/mybloxx-october-systemwide.pac`
- `ProxyType = Auto`
- `ProxyPACFallbackAllowed = true`
- `ProxyCaptiveLoginAllowed = true`
- `com.apple.dnsSettings.managed`
- DNS-over-HTTPS: `https://freedns.controld.com/x-hagezi-pro`
- `AllowFailover = false`
- `ProhibitDisablement = false`

## PAC design

The October PAC is intentionally compact compared with the failed megabyte-scale September experiment.

It currently combines:

- explicit host rules from the original MYbloXX PAC
- a current high-confidence subset of HaGeZi LIGHT
- major ad networks such as DoubleClick, Google Syndication, Criteo, Taboola, Outbrain, PubMatic, Rubicon, OpenX, Amazon Ads, and others

The host table is minimized by parent domain.

Blocking behavior:

- blocked host → `PROXY 127.0.0.1:8021`
- ordinary host → `DIRECT`
- `shop.tiktok.com` → explicit `DIRECT` before block evaluation

No third-party browsing proxy receives ordinary web traffic.

## Why hybrid

The DNS-only October profile remains available as a fallback:

`MYbloXX-October-Refresh-2026-HaGeZi-Pro-TikTok-Compatible.mobileconfig`

The hybrid profile is recommended when the goal is broader blocking on both Wi-Fi and cellular, especially when Private Relay / Limit IP Address Tracking is enabled.

Apple Global HTTP Proxy applies to HTTP/HTTPS traffic that uses the system proxy path across Wi-Fi and cellular. It does not filter every possible packet or protocol. Apps using non-HTTP protocols, custom sockets, or networking that bypasses the system HTTP proxy can still escape PAC filtering.

The DNS layer adds coverage for apps that use system DNS, but Private Relay or app-specific encrypted DNS can change that path.

## Verification

After installing the hybrid profile:

1. Remove the older October DNS-only profile first to avoid two competing managed-DNS profiles.
2. Confirm the new profile is installed under **VPN & Device Management**.
3. Under DNS Settings, select **MYbloXX — HaGeZi Pro DNS** if iOS exposes it as selectable.
4. Test `https://pagead2.googlesyndication.com` — it should fail.
5. Test the same ad-heavy page once on Wi-Fi and once on cellular.
6. Confirm `https://shop.tiktok.com` and TikTok Shop continue to work.

## Safety / availability tradeoff

`ProxyPACFallbackAllowed = true` is intentional. If the PAC URL cannot be fetched temporarily, normal web access can continue instead of the device effectively losing HTTP/HTTPS connectivity. The downside is that filtering can temporarily fail open during a PAC fetch/evaluation failure.

## Project history

The repository name still contains “september-refresh” for continuity. Git history retains the September experiments, but the October Systemwide Hybrid profile is the current recommended build.
