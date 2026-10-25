"""Build trimmed geosite.dat / geoip.dat for the Happ routing profile.

Downloads the latest full databases from Loyalsoldier/v2ray-rules-dat and keeps
only the categories listed below, so Happ downloads a few hundred KB instead of
tens of MB. Entries are copied byte-for-byte from the source files.

Usage: python3 build.py
"""

import urllib.request

SOURCE = "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/"

# Must cover every geosite:/geoip: tag referenced by the GeoRU routing profile.
GEOSITE_TAGS = {
    "apple", "apple-cn", "apple-dev", "apple-intelligence", "apple-pki",
    "apple-tvplus", "apple-update",
    "category-ads",
    "category-bank-ru", "category-betting-ru", "category-ecommerce-ru",
    "category-entertainment-ru", "category-gov-ru", "category-media-ru",
    "category-media-ru-blocked", "category-medicine-ru", "category-retail-ru",
    "category-ru", "category-travel-ru",
    "genotek-ru", "ideco-ru", "mailru-group", "mts-ru", "myoffice-ru", "yandex",
}
GEOIP_TAGS = {"ru"}


def read_varint(buf, pos):
    result = shift = 0
    while True:
        byte = buf[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            return result, pos


def write_varint(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def entries(buf):
    """Yield (tag, raw_entry) for each top-level entry (field 1) of a *List message."""
    pos = 0
    while pos < len(buf):
        key, pos = read_varint(buf, pos)
        length, pos = read_varint(buf, pos)
        raw = buf[pos:pos + length]
        pos += length
        if key != 0x0A:  # field 1, length-delimited
            continue
        # Field 1 of GeoSite / GeoIP is the country_code (tag) string.
        k, p = read_varint(raw, 0)
        n, p = read_varint(raw, p)
        yield raw[p:p + n].decode().lower(), raw


def trim(name, wanted):
    with urllib.request.urlopen(SOURCE + name, timeout=300) as resp:
        data = resp.read()
    out = bytearray()
    found = {}
    for tag, raw in entries(data):
        if tag in wanted:
            out += b"\x0a" + write_varint(len(raw)) + raw
            found[tag] = raw
    missing = wanted - found.keys()
    if missing:
        raise SystemExit(f"{name}: categories missing in source: {sorted(missing)}")
    with open(name, "wb") as f:
        f.write(out)
    print(f"{name}: {len(found)} categories, {len(out)} bytes (source {len(data)} bytes)")


if __name__ == "__main__":
    trim("geosite.dat", GEOSITE_TAGS)
    trim("geoip.dat", GEOIP_TAGS)
