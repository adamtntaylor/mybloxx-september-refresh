# MYbloXX iOS DNS Refresh

Current active build: **October 2026 — HaGeZi Pro (TikTok Compatible)**

This project now follows the architecture that proved reliable on the iPhone in August/September 2026: a single managed encrypted-DNS payload using HaGeZi Pro through Control D.

## Current profile

Install:

`MYbloXX-October-Refresh-2026-HaGeZi-Pro-TikTok-Compatible.mobileconfig`

The profile contains one payload:

- `com.apple.dnsSettings.managed`
- DNS-over-HTTPS
- Server: `https://freedns.controld.com/x-hagezi-pro`
- `AllowFailover = false`
- `ProhibitDisablement = false`

## Why DNS-only

The earlier September PAC experiment is retired from the active project. The working DNS-only design is intentionally simpler:

- no Global HTTP Proxy
- no PAC JavaScript
- no localhost sinkhole
- no locally compiled 50k–70k domain table
- no GitHub Actions job required to rebuild blocklists

Control D serves the current HaGeZi Pro resolver directly, so upstream list maintenance happens without regenerating or reinstalling this profile.

## TikTok compatibility

The Pro tier is deliberately retained instead of Pro++ or Ultimate because it balances strong ad/tracker blocking with a lower risk of breaking app functionality and referral links. The August build using the same endpoint worked reliably with TikTok.

This fixed public resolver cannot provide a user-specific per-domain allowlist. If TikTok Shop ever becomes blocked upstream, the correct fix is to reassess the resolver/tier rather than bolt a second PAC layer onto this profile.

## Verification

After installation:

1. In iOS DNS Settings, select **MYbloXX DNS — HaGeZi Pro (October 2026)**.
2. Open `https://controld.com/status` in Safari and confirm Control D is in use.
3. Test a known ad-serving hostname such as `https://pagead2.googlesyndication.com`; it should fail to load.
4. Confirm `https://shop.tiktok.com` and the TikTok app still work normally.

Note: the bare `doubleclick.net` domain is not a reliable block test because HaGeZi intentionally allows some referral/link-tracking domains depending on tier.

## Project history

The repository name still contains “september-refresh” for continuity. Git history retains the retired PAC experiments, but the current supported configuration is the DNS-only October profile above.
