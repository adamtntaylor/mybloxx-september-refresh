// MYbloXX September Refresh 2026 — Mullvad Mobile PAC
// Auto-generated from OISD Small, Mullvad custom ads/trackers, and AdGuard Mobile.
// Aggressive TikTok-specific tracker lists are intentionally excluded.
var BLOCK={};
var ALLOW={};
var BLOCKED="PROXY 127.0.0.1:8021";
var DIRECT="DIRECT";
function suffixMatch(t,h){if(t[h])return true;var p=h.indexOf(".");while(p>0){h=h.substring(p+1);if(t[h])return true;p=h.indexOf(".");}return false;}
function localHost(h){if(!h||isPlainHostName(h))return true;if(h=="localhost"||dnsDomainIs(h,".local")||dnsDomainIs(h,".lan")||dnsDomainIs(h,".home.arpa"))return true;if(/^127\./.test(h)||/^10\./.test(h)||/^192\.168\./.test(h))return true;var m=/^172\.(\d+)\./.exec(h);return !!(m&&Number(m[1])>=16&&Number(m[1])<=31);}
function FindProxyForURL(url,host){host=(host||"").toLowerCase().replace(/\.$/,"");if(localHost(host))return DIRECT;if(suffixMatch(ALLOW,host))return DIRECT;if(suffixMatch(BLOCK,host))return BLOCKED;return DIRECT;}
