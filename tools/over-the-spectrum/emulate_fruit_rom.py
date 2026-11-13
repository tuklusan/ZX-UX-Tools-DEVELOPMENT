#!/usr/bin/env python3
"""Load the original OTS cassette-1 side A TZX in the bundled 48K Spectrum ROM emulator.

No BASIC export or text converter is used for the load. Keyboard enters LOAD "" into
Sinclair 48K BASIC and the ROM tape loader receives original tape header and data
records through zxmachine's fast cassette trap, then LIST commands are issued.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent
EMULATOR = ROOT/'tools'/'spectrum_emulator'
if not (EMULATOR/'zxmachine.py').exists():
    with __import__('zipfile').ZipFile(ROOT/'tools'/'spectrum_emulator.zip') as archive:
        archive.extractall(ROOT/'tools')
sys.path.insert(0, str(EMULATOR))
sys.path.insert(0, str(ROOT/'tools'))
from zxmachine import Machine
from zxscreen import write_png
from extract_ots_basic import load_converter

OUT=ROOT/'emulator_fruit'
OUT.mkdir(exist_ok=True)
conv=load_converter()
blocks=list(conv.tzx_blocks((ROOT/'OverTheSpectrumCassette1_SideA.tzx').read_bytes()))
assert blocks[0][0] == 0 and blocks[0][2:7].lower() == b'fruit'
assert blocks[1][0] == 0xff
m=Machine()
# Boot the actual Sinclair 48K ROM to the BASIC cursor.
for _ in range(300): m.run_frame()
m.cassette = blocks[:2].copy()
def tap(combo, hold=4, release=9):
    m.press(combo)
    for _ in range(hold):m.run_frame()
    m.press([])
    for _ in range(release):m.run_frame()

def shot(name):
    write_png(m.screen(),str(OUT/name),border=m.border,scale=3)

def word(a):
    return m.mem[a] | (m.mem[a+1]<<8)

# On the actual Sinclair 48K keyboard J in keyword mode = LOAD.
# Symbol Shift + P = ", and ENTER executes the command.
for combo in [('j',),('SS','p'),('SS','p'),('ENTER',)]:tap(combo)
for _ in range(70):m.run_frame()
print('LOAD completed (ROM BASIC cursor):', 'tape blocks remaining', len(m.cassette), 'frame', m.frame)
print('PROG/VARS/E_LINE', hex(word(0x5c53)),hex(word(0x5c4b)),hex(word(0x5c59)))
shot('01-after-load.png')

# check raw original line numbers in machine RAM directly, independent of exporter
prog=word(0x5c53)
vars=word(0x5c4b)
raw=bytes(m.mem[prog:vars])
expected=blocks[1][1:-1]
vars_offset=int.from_bytes(blocks[0][16:18],'little')
print('ROM-RAM loaded data equals original TZX data:',raw == expected[:vars_offset],len(raw),vars_offset)

# Now type LIST 5500 as a Spectrum command. K=LIST in K mode.
def enter_list(n):
    tap(('k',))
    for char in str(n):
        tap((char,))
    tap(('ENTER',))
    for _ in range(30):m.run_frame()

enter_list(5500)
shot('02-list-5500.png')
print('After LIST 5500 PC',hex(m.cpu.pc),'frame',m.frame)
# Scroll up a page if the ROM asks for a key; or list at 8000 from BASIC ready state
# Exit the ROM's "scroll?" pagination and inspect the end of the tape listing.
tap(('n',))
for _ in range(25):m.run_frame()
enter_list(8350)
shot('04-list-8350.png')

# Report actual RAM line numbers used by Sinclair BASIC, as physically loaded
p=0
numbers=[]
while p<len(raw):
    if p+4>len(raw): raise RuntimeError('bad line header')
    n=int.from_bytes(raw[p:p+2],'big')
    sz=int.from_bytes(raw[p+2:p+4],'little')
    numbers.append(n)
    p+=4+sz
if p!=len(raw): raise RuntimeError(f'bad line bytes: {p} != {len(raw)}')
print('line count',len(numbers))
for a,b in [(5500,5600),(5700,5840),(7000,7120),(8000,8460),(9900,9999)]:
 print('line range',a,b, [n for n in numbers if a<=n<=b])
print('ROM screen images in',OUT)
