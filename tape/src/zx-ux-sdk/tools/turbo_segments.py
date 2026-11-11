"""Boot-only ZX-UX TZX segment framing (not userland tape I/O).

The tape carries the loading screen (a 6912-byte SCREEN$, loaded straight into
display memory) and then the image, cut into 24 parts: 25 TZX turbo blocks in
all. Each block holds its bytes followed by one parity byte (so the XOR of the
whole block is zero), which is the block format of the turbo loader that
receives them (turbo_boot.asm, turbo_loader.bin). The loader reads each block
straight to its final address and needs no header, ordinal or CRC.

This module is intentionally a packet generator, not a substitute for a
genuine speed/ROM/FUSE load test.  A caller must provide separately checked
bootstrap and BASIC blocks before a bootable TZX can be considered.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct

COUNT = 24
# Strictly less than 38,000 decimal bytes (not a 38 KiB approximation).
MAX_TZX_BYTES = 38_000
LOAD_BASE = 0x5D98
ENTRY = 0x6000
SCREEN_BASE = 0x4000
SCREEN_SIZE = 6912                   # 6144 bytes of bitmap and 768 of attributes
# pilot, sync1, sync2, zero, one, pilot pulses: the timings the turbo loader is built for. A data bit is two
# pulses of the zero (428) or one (855) length, so a bit takes 856 or 1710 T-states, 1283 on average: twice
# the ROM's rate (855 and 1710 per pulse, 2565 on average), 2728 bits a second. The loader needs about 165 pilot
# pulses (it waits 23 ms after the first edge, then counts 60 good pairs); 494 pulses are three times that.
# The blocks follow each other with no gap (PAUSE_MS), so the pilot is also the time the bootstrap has to draw
# a progress row (about 15 ms) between two blocks: the pilot lasts 494 * 2042 T-states = 288 ms.
TIMINGS = (2042, 875, 613, 428, 855, 494)
PAUSE_MS = 0
# The pause after each of the four ROM-standard blocks. After the bootstrap's data there is none: the pilot of
# the first turbo block follows at once.
ROM_PAUSES = (1000, 1000, 1000, 0)


class TurboFormatError(ValueError):
    """A malformed, missing, or misordered boot segment."""


def xor_bytes(data: bytes) -> int:
    value = 0
    for b in data:
        value ^= b
    return value


def layout(image_length: int, *, load_base: int = LOAD_BASE):
    if not 0 < image_length <= 0xffff:
        raise TurboFormatError('image length outside 16-bit transport')
    if not 0 <= load_base < ENTRY < load_base + image_length <= 0xce00:
        raise TurboFormatError('load and entry must fit below protected boot stack')
    q, r = divmod(image_length, COUNT)
    if not q:
        raise TurboFormatError('image too short for 24 nonempty segments')
    sizes = [q + (i < r) for i in range(COUNT)]
    offsets = []
    position = 0
    for size in sizes:
        offsets.append((position, size))
        position += size
    assert position == image_length
    return tuple(offsets)


def make_segments(image: bytes, *, load_base: int = LOAD_BASE):
    """The 24 blocks: each part's bytes followed by their XOR (so the XOR of a block is zero)."""
    if not isinstance(image, bytes):
        raise TypeError('image must be bytes')
    blocks = []
    for offset, size in layout(len(image), load_base=load_base):
        data = image[offset:offset+size]
        blocks.append(data + bytes((xor_bytes(data),)))
    return tuple(blocks)


def pack_turbo_record(packet: bytes, *, pause_ms: int) -> bytes:
    if not 0 <= pause_ms <= 0xffff:
        raise TurboFormatError('turbo pause outside TZX unsigned 16-bit value')
    if not isinstance(packet, bytes):
        raise TypeError('packet must be bytes')
    if not 2 <= len(packet) <= 0xffffff:
        raise TurboFormatError('invalid turbo record length')
    pilot, sync1, sync2, zero, one, count = TIMINGS
    return (bytes([0x11]) + struct.pack('<HHHHHHBH', pilot, sync1, sync2,
                                       zero, one, count, 8, pause_ms)
            + len(packet).to_bytes(3, 'little') + packet)


def read_packet(packet: bytes, *, size: int) -> bytes:
    """Fail closed: the block must be size bytes and a parity byte, XOR zero."""
    if len(packet) != size + 1:
        raise TurboFormatError('segment length mismatch')
    if xor_bytes(packet) != 0:
        raise TurboFormatError('segment XOR mismatch')
    return packet[:-1]


def read_segments(packets, *, image_length: int, load_base: int = LOAD_BASE) -> bytes:
    plan = layout(image_length, load_base=load_base)
    if len(packets) != COUNT:
        raise TurboFormatError('expected exactly 24 segments')
    result = bytearray(image_length)
    for (offset, size), packet in zip(plan, packets):
        result[offset:offset+size] = read_packet(packet, size=size)
    return bytes(result)


def pack_standard_tzx_block(block: bytes, pause_ms: int) -> bytes:
    if not 0 <= pause_ms <= 0xffff or not 2 <= len(block) <= 0xffff:
        raise TurboFormatError('invalid ROM-standard block')
    if xor_bytes(block):
        raise TurboFormatError('ROM-standard block parity failed')
    return b'\x10' + struct.pack('<HH', pause_ms, len(block)) + block


def make_screen_block(screen: bytes) -> bytes:
    """The loading screen as a block: its bytes followed by their XOR."""
    if not isinstance(screen, bytes) or len(screen) != SCREEN_SIZE:
        raise TurboFormatError('the loading screen must be 6912 bytes')
    return screen + bytes((xor_bytes(screen),))


def pack_tzx(basic_pair, bootstrap_pair, screen: bytes, image: bytes, *, pause_ms: int,
             load_base: int = LOAD_BASE) -> bytes:
    """Frame four ROM 10h records, then the screen block and the 24 image blocks (turbo 11h records).

    Strictly framing only: successful construction is NOT runtime validation
    of the separately provided ROM-standard BASIC/bootstrap code.
    """
    if len(basic_pair) != 2 or len(bootstrap_pair) != 2:
        raise TurboFormatError('two ROM header/data pairs are required')
    records = [pack_standard_tzx_block(block, gap) for block, gap in
               zip((*basic_pair, *bootstrap_pair), ROM_PAUSES)]
    records.append(pack_turbo_record(make_screen_block(screen), pause_ms=pause_ms))
    records.extend(pack_turbo_record(p, pause_ms=pause_ms) for p in
                   make_segments(image, load_base=load_base))
    tape = b'ZXTape!' + bytes((0x1a, 0x01, 0x14)) + b''.join(records)
    if len(tape) >= MAX_TZX_BYTES:
        raise TurboFormatError('boot TZX must be smaller than 38,000 bytes')
    return tape
