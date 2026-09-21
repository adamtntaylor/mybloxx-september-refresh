// MYbloXX September Refresh — PAC diagnostic
// Deliberately tiny. Used only to verify that iOS is executing the Global HTTP Proxy PAC.
var BLOCKED="PROXY 127.0.0.1:8021";
var DIRECT="DIRECT";

function hostIs(host, domain) {
  host=(host||"").toLowerCase().replace(/\.$/,"");
  domain=domain.toLowerCase();
  return host===domain || dnsDomainIs(host, "."+domain);
}

function FindProxyForURL(url, host) {
  host=(host||"").toLowerCase().replace(/\.$/,"");

  // Preserve the user's explicit TikTok Shop exception.
  if (hostIs(host,"shop.tiktok.com")) return DIRECT;

  // Canary: this MUST fail if the PAC is actually executing.
  if (hostIs(host,"example.com")) return BLOCKED;

  // High-confidence Google ad infrastructure.
  if (hostIs(host,"doubleclick.net")) return BLOCKED;
  if (hostIs(host,"googlesyndication.com")) return BLOCKED;
  if (hostIs(host,"googleadservices.com")) return BLOCKED;
  if (hostIs(host,"googletagservices.com")) return BLOCKED;
  if (hostIs(host,"adservice.google.com")) return BLOCKED;
  if (hostIs(host,"2mdn.net")) return BLOCKED;

  return DIRECT;
}
