#!/usr/bin/env python3

import hashlib
import sys
import zlib

NINTENDO = (
    b"\x24\xff\xae\x51\x69\x9a\xa2\x21\x3d\x84\x82\x0a\x84\xe4\x09\xad"
    b"\x11\x24\x8b\x98\xc0\x81\x7f\x21\xa3\x52\xbe\x19\x93\x09\xce\x20"
    b"\x10\x46\x4a\x4a\xf8\x27\x31\xec\x58\xc7\xe8\x33\x82\xe3\xce\xbf"
    b"\x85\xf4\xdf\x94\xce\x4b\x09\xc1\x94\x56\x8a\xc0\x13\x72\xa7\xfc"
    b"\x9f\x84\x4d\x73\xa3\xca\x9a\x61\x58\x97\xa3\x27\xfc\x03\x98\x76"
    b"\x23\x1d\xc7\x61\x03\x04\xae\x56\xbf\x38\x84\x00\x40\xa7\x0e\xfd"
    b"\xff\x52\xfe\x03\x6f\x95\x30\xf1\x97\xfb\xc0\x85\x60\xd6\x80\x25"
    b"\xa9\x63\xbe\x03\x01\x4e\x38\xe2\xf9\xa2\x34\xff\xbb\x3e\x03\x44"
    b"\x78\x00\x90\xcb\x88\x11\x3a\x94\x65\xc0\x7c\x63\x87\xf0\x3c\xaf"
    b"\xd6\x25\xe4\x8b\x38\x0a\xac\x72\x21\xd4\xf8\x07"
)

JPN = "Japan"
USA = "USA"
EUR = "Europe"

NES = "nes"
SMS = "sms"

HUDSON = "Hudson Best Collection"
JALECO = "Jaleco Collection"
CAPCOM = "Capcom Classics Mini Mix"
PHSTAR = "Phantasy Star Collection"

GBA = {
    "HUBEST_VOL01B7IJ": [
        (0x22390, NES, JPN, HUDSON, "Bomberman"),
        (0x283A0, NES, JPN, HUDSON, "Bomberman II"),
    ],
    "HUBEST_VOL02B72J": [
        (0x2E474, NES, JPN, HUDSON, "Lode Runner"),
        (0x34484, NES, JPN, HUDSON, "Championship Lode Runner"),
    ],
    "HUBEST_VOL03B73J": [
        (0x28130, NES, JPN, HUDSON, "Challenger"),
        (0x32140, NES, JPN, HUDSON, "Meikyuu Kumikyoku - Milon no Daibouken"),
    ],
    "HUBEST_VOL04B74J": [
        (0x2CED4, NES, JPN, HUDSON, "Nuts & Milk"),
        (0x32EE4, NES, JPN, HUDSON, "Binary Land"),
        (0x38EF4, NES, JPN, HUDSON, "Salad no Kuni no Tomato Hime"),
    ],
    # "HUBEST_VOL05B75J": [
    #     (0x00000, NES, JPN, HUDSON, "Star Force"),
    #     (0x00000, NES, JPN, HUDSON, "Star Soldier"),
    #     (0x00000, NES, JPN, HUDSON, "Hector '87"),
    # ],
    "HUBEST_VOL06B76J": [
        (0x38248, NES, JPN, HUDSON, "Takahashi Meijin no Bouken-jima"),
        (0x48258, NES, JPN, HUDSON, "Takahashi Meijin no Bouken-jima II"),
        (0x88268, NES, JPN, HUDSON, "Takahashi Meijin no Bouken-jima III"),
        (0xc8278, NES, JPN, HUDSON, "Takahashi Meijin no Bouken-jima IV"),
    ],
    "SHINJAJA\0\0\0\0BNJJ": [
        (0x23B20, NES, JPN, JALECO, "Jajamaru no Daibouken"),  # not working
        (0x1BAE0, NES, JPN, JALECO, "Ninja Jajamaru-kun"),
        (0x07A20, NES, JPN, JALECO, "Exerion"),
        (0x13AA0, NES, JPN, JALECO, "City Connection"),
        (0x0DA60, NES, JPN, JALECO, "Formation Z"),
    ],
    # "MOERO JALECOBJCJ": [
    #     (0x00000, NES, JPN, JALECO, "Moero!! Pro Yakyuu"),
    #     (0x00000, NES, JPN, JALECO, "Moero!! Pro Yakyuu '88 - Ketteiban"),
    #     (0x00000, NES, JPN, JALECO, "Moero!! Pro Soccer"),
    #     (0x00000, NES, JPN, JALECO, "Moero!! Pro Tennis"),
    #     (0x00000, NES, JPN, JALECO, "Moero!! Junior Basket - Two on Two"),
    #     (0x00000, NES, JPN, JALECO, "Moero!! Juudou Warriors"),
    # ],
    # "CAPCOMINIMIXBC6E": [
    #     (0x000000, NES, USA, CAPCOM, "Strider"),
    #     (0x000000, NES, USA, CAPCOM, "Mighty Final Fight"),
    #     (0x000000, NES, USA, CAPCOM, "Bionic Commando"),
    # ],
    "PHANTASYSTARAYCE": [
        (0x7722D4, SMS, USA, PHSTAR, "Phantasy Star", 512 * 1024),
    ],
    # "PHANTASYSTARAYCP": [
    #     (0x000000, SMS, EUR, PHSTAR, "Phantasy Star", 512 * 1024),
    # ],
}


def main():
    assert len(sys.argv) == 2, f"usage: {sys.argv[0]} ROM.gba"
    _, path = sys.argv
    with open(path, "rb") as f:
        data = f.read()
    assert data[0x04:0xA0] == NINTENDO, f"{path}: not a GBA ROM"

    title = data[0xA0:0xB0].decode("latin-1")
    toc = GBA.get(title)
    assert toc, f"{title}: unknown GBA ROM"

    for n, entry in enumerate(toc):
        if n:
            print()

        seek, ext, region, group, title = entry[:5]
        full_title = f"{title} ({region}) ({group})"
        print(f"- title: {full_title}")

        reader = {
            NES: read_nes,
            SMS: read_sms,
        }[ext]
        header, headerless = reader(path, data, seek, *entry[5:])

        if header:
            rom = header + headerless
            cksum("headered", rom)
            print(f"    header: {" ".join('%02x' % x for x in header)}")
            cksum("headerless", headerless)
        else:
            rom = headerless
            cksum("rom", rom)

        with open(f"{full_title}.{ext}", "wb") as f:
            f.write(rom)


def read_nes(path, data, seek):
    header = data[seek : seek + 16]
    magic = header[:4]
    assert magic == b"NES\x1a", f"{path}: {seek}: iNES header not found"

    prg_size = header[4] * 16384
    chr_size = header[5] * 8192
    size = 16 + prg_size + chr_size

    headerless = data[seek + 16 : seek + size]
    return header, headerless


def read_sms(path, data, seek, size):
    rom = data[seek : seek + size]
    header = rom[0x7FF0:0x7FF8]
    magic = header[:8]
    assert magic == b"TMR SEGA", f"{path}: {seek}: SMS header not found"
    return None, rom


def cksum(name, data):
    print(f"  {name}:")
    print(f"    size: {len(data)}")
    print(f"    crc32: {zlib.crc32(data):08x}")
    print(f"    md5: {hashlib.md5(data).hexdigest()}")
    print(f"    sha1: {hashlib.sha1(data).hexdigest()}")
    print(f"    sha256: {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
