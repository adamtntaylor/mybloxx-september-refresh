# MYbloXX September Refresh 2026

MYbloXX-style system-wide ad/tracker blocking for a **supervised iPhone**.

## Permanent PAC URL

`https://raw.githubusercontent.com/adamtntaylor/mybloxx-september-refresh/main/mybloxx-september-refresh.pac`

The installed iPhone profile can keep using this URL while the PAC contents are refreshed in place.

## Blocklist design

This mobile-focused PAC uses source families currently trusted by Mullvad while intentionally excluding Mullvad's aggressive TikTok-specific tracker list:

- OISD Small
- Mullvad custom advertising rules
- Mullvad custom tracker rules
- AdGuard Mobile ad-server rules

The published PAC currently contains about **57,000+ minimized host rules** and uses the original MYbloXX-style local sinkhole behavior:

- blocked host → `PROXY 127.0.0.1:8021`
- allowed/ordinary host → `DIRECT`

No third-party HTTP proxy receives normal browsing traffic.

## TikTok Shop exception

`shop.tiktok.com` is explicitly allowlisted. The allowlist is evaluated **before** the blocklist, so a parent-domain block cannot override this PAC exception.

## iPhone profile

Install:

`MYbloXX-September-Refresh-2026-Mullvad-Mobile.mobileconfig`

It contains two payloads:

1. **Global HTTP Proxy** — the actual MYbloXX-style system-wide PAC blocker.
2. **Encrypted DNS** — unfiltered Cloudflare DoH, user-disableable, so the DNS configuration remains visible/toggleable in iOS settings without creating a second ad-blocking layer that could defeat PAC exceptions.

Remove any older MYbloXX Global HTTP Proxy profile before installing this one because iOS supports only one Global HTTP Proxy payload at a time.

## Automatic refresh

`.github/workflows/refresh-pac.yml` rebuilds the PAC daily from current upstream sources and commits it only when the generated PAC changes.
