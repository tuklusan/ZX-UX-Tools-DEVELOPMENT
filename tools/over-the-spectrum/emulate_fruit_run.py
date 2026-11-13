#!/usr/bin/env python3
"""Run the untouched cassette-1A Fruit Machine on the Sinclair 48K ROM emulator.

Captures start/idle and one ENTER-started turn, without changing tape or BASIC.
Uses the same preserved fast cassette trap as emulate_fruit_rom.py.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
EMULATOR=ROOT/'tools'/'spectrum_emulator'
if not (EMULATOR/'zxmachine.py').exists():
    with __import__('zipfile').ZipFile(ROOT/'tools'/'spectrum_emulator.zip') as archive:
        archive.extractall(ROOT/'tools')
sys.path.insert(0,str(EMULATOR))
sys.path.insert(0,str(ROOT/'tools'))
from zxmachine import Machine
from zxscreen import write_png
from extract_ots_basic import load_converter
OUT=ROOT/'emulator_fruit'
OUT.mkdir(exist_ok=True)
conv=load_converter()
blocks=list(conv.tzx_blocks((ROOT/'OverTheSpectrumCassette1_SideA.tzx').read_bytes()))
assert blocks[0][0]==0 and blocks[0][2:7].lower()==b'fruit'
assert blocks[1][0]==0xff
m=Machine()
for _ in range(300):m.run_frame()
m.cassette=blocks[:2].copy()
def tap(combo,hold=4,release=9):
    m.press(combo)
    for _ in range(hold):m.run_frame()
    m.press([])
    for _ in range(release):m.run_frame()
def shot(name):
    write_png(m.screen(),str(OUT/name),border=m.border,scale=3)
for combo in [('j',),('SS','p'),('SS','p'),('ENTER',)]:tap(combo)
for _ in range(70):m.run_frame()
print('post-load',hex(m.cpu.pc),'blocks',len(m.cassette),'frame',m.frame,flush=True)
shot('fruit-after-load.png')
tap(('r',))
tap(('ENTER',))
for stage,frames in [('initial',300),('ready',700)]:
    for _ in range(frames):m.run_frame()
    print(stage,hex(m.cpu.pc),'frame',m.frame,flush=True)
    shot(f'fruit-{stage}.png')
tap(('ENTER',))
for stage,frames in [('turn1',350),('turn2',700)]:
    for _ in range(frames):m.run_frame()
    print(stage,hex(m.cpu.pc),'frame',m.frame,flush=True)
    shot(f'fruit-{stage}.png')
