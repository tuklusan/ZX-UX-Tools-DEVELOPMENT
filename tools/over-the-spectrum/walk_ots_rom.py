#!/usr/bin/env python3
"""Keyboard-driven Sinclair ROM walkthroughs for standalone Over the Spectrum TZXs.

All input goes through ZX Spectrum's real keyboard matrix. TZX is loaded by
ROM LOAD "" with the emulator's fast cassette trap (not injected BASIC).
Every test records exact key combinations, frame timings, screenshots, and
BASIC load fidelity. The original TZX, book, and BAS are read-only.

Usage: python3 tools/walk_ots_rom.py {loadall,leapfrog,reversal,frog,fruit}
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parent.parent
EMULATOR=ROOT/'tools'/'spectrum_emulator'
if not (EMULATOR/'zxmachine.py').exists():
    with zipfile.ZipFile(ROOT/'tools'/'spectrum_emulator.zip') as archive:
        archive.extractall(ROOT/'tools')
sys.path[:0]=[str(EMULATOR),str(ROOT/'tools')]
from zxmachine import Machine
from zxscreen import write_png
from extract_ots_basic import load_converter
CONV=load_converter()
FILES={
    'fruit':'OTS_tape_1_side_A_fruit/fruit.tzx',
    'leapfrog':'OTS_tape_3_side_A_leapfrog/leapfrog.tzx',
    'reversal':'OTS_tape_3_side_A_reversal/reversal.tzx',
    'frogshapes':'OTS_tape_2_side_B_frogshapes/frogshapes.tzx',
    'f-way-frog':'OTS_tape_2_side_B_f-way-frog/f-way-frog.tzx',
}
FILES.update({p.stem:str(p.relative_to(ROOT/'tapes')) for p in (ROOT/'tapes').glob('*/*.tzx')})

class Session:
    def __init__(self,case):
        self.case=case
        self.m=Machine()
        self.out=ROOT/f'emulator_{case}'
        self.out.mkdir(exist_ok=True)
        self.events=[]
        self.wait(300,'ROM boot')

    def emit(self,kind,detail):
        msg=f'frame={self.m.frame:6d} | {kind:8s} | {detail}'
        self.events.append(msg)
        print(msg,flush=True)

    def wait(self,n,why):
        for _ in range(n):self.m.run_frame()
        self.emit('wait',f'{n} frames: {why}')

    def tap(self,combo,hold=4,release=9):
        self.emit('press','+'.join(combo)+f' (hold {hold}, release {release} frames)')
        self.m.press(combo)
        for _ in range(hold):self.m.run_frame()
        self.m.press([])
        for _ in range(release):self.m.run_frame()

    def screen(self,name):
        file=self.out/f'{name}.png'
        write_png(self.m.screen(),str(file),border=self.m.border,scale=3)
        self.emit('screen',file.name)

    def text(self,characters):
        for char in characters:
            if char=='\n':self.tap(('ENTER',))
            elif char==' ':self.tap(('SPACE',))
            elif char.isdigit() or char.islower():self.tap((char,))
            else:raise ValueError(f'Unsupported direct text key: {char!r}')

    def load(self,name,capture=True):
        tape=(ROOT/'tapes'/FILES[name]).read_bytes()
        blocks=list(CONV.tzx_blocks(tape))
        assert len(blocks)==2 and blocks[0][0]==0 and blocks[0][1]==0 and blocks[1][0]==0xff
        self.m.cassette=blocks.copy()
        for combo in [('j',),('SS','p'),('SS','p'),('ENTER',)]:self.tap(combo)
        self.wait(70,f'finish ROM LOAD "" for {name}')
        m=self.m.mem
        word=lambda a:m[a]|(m[a+1]<<8)
        prog,vars=word(0x5c53),word(0x5c4b)
        limit=int.from_bytes(blocks[0][16:18],'little')
        expected=blocks[1][1:1+limit]
        actual=bytes(m[prog:vars])
        same=(actual==expected)
        self.emit('ROM-load',f'{name} exact BASIC bytes={same} ({len(actual)}), tape blocks left={len(self.m.cassette)}')
        if not same:raise AssertionError(f'{name}: ROM loaded bytes differ')
        if capture:self.screen(f'{name}-loaded')

    def run(self):
        self.tap(('r',))
        self.tap(('ENTER',))

def main(case):
    if case=='loadall':
        good=[]
        for name in sorted(FILES):
            s=Session('loadall')
            s.load(name,capture=False)
            good.append(name)
        print(f'All {len(good)} individual tapes ROM-loaded with exact byte matches',flush=True)
        return None
    s=Session(case)
    if case=='fruit':
        s.load('fruit')
        s.run()
        s.wait(300,'original initial screen')
        s.screen('initial')
        s.wait(700,'ready for turn')
        s.screen('ready')
        s.tap(('ENTER',))
        s.wait(350,'turn in progress')
        s.screen('turn1')
        s.wait(700,'turn later')
        s.screen('turn2')
    elif case=='leapfrog':
        s.load('leapfrog')
        s.run()
        s.wait(240,'board and first INPUT prompt')
        s.screen('first-prompt')
        s.text('45\n')
        s.wait(220,'move 4 to 5')
        s.screen('after-45')
        s.text('64\n')
        s.wait(220,'move 6 to 4')
        s.screen('after-64')
    elif case=='reversal':
        s.load('reversal')
        s.run()
        s.wait(250,'random initial 9-number arrangement, numeric INPUT')
        s.screen('initial-prompt')
        s.text('3\n')
        s.wait(280,'reverse first 3; new INPUT prompt')
        s.screen('after-3')
        s.text('0\n')
        s.wait(160,'STOP request')
        s.screen('stopped')
    elif case=='frog':
        s.load('frogshapes')
        s.run()
        s.wait(900,'graphics setup before STOP')
        s.screen('shapes-finished')
        # The setup program ends with STOP; use the BASIC command line to load
        # the *separate* f-way-frog tape, preserving preloaded graphic bytes.
        s.load('f-way-frog')
        s.run()
        s.wait(600,'frog game initial board')
        s.screen('game-start')
        s.tap(('q',),hold=80,release=12)
        s.wait(160,'frog up input')
        s.screen('after-q')
        s.tap(('p',),hold=80,release=12)
        s.wait(160,'frog right input')
        s.screen('after-p')
    return s

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('case',choices=['loadall','fruit','leapfrog','reversal','frog'])
    a=p.parse_args()
    main(a.case)
