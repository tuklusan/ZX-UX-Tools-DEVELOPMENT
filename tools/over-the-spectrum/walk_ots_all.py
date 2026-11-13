#!/usr/bin/env python3
"""Reproducible human-style keyboard sessions for all 29 OverTheSpectrum recordings.

Use the real Sinclair 48K ROM via the ZX-UX rvm emulator; each source is a
standalone TZX cut from the original tape. All commands use keyboard scan and
ROM cassette LOAD trap. Screenshots and transcripts are outputs only; no
program or original tape bytes are patched. Set --case to run one session.

The emulator is deterministic with its initial state, but RND, clock timers,
scan timing, etc. should be treated as variable across independent runs.
"""
from __future__ import annotations
import argparse, json, sys, re
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
EMU = ROOT/'tools'/'spectrum_emulator'
if not (EMU/'zxmachine.py').exists():
    with zipfile.ZipFile(ROOT/'tools'/'spectrum_emulator.zip') as z:z.extractall(ROOT/'tools')
sys.path[:0]=[str(EMU),str(ROOT/'tools')]
from zxmachine import Machine
from zxscreen import write_png
from extract_ots_basic import load_converter
CONV=load_converter()
FILES={p.stem:p for p in (ROOT/'tapes').glob('*/*.tzx')}

class Session:
    def __init__(self,case, *, reuse=None):
        self.case=case
        self.m=reuse or Machine()
        self.dir=ROOT/'sessions'/case
        self.dir.mkdir(parents=True,exist_ok=True)
        self.events=[];self.captures=[];self.load_details=[]
        if reuse is None:self.wait(300,'48K ROM initial boot')
    def log(self,event,description):
        obj=dict(frame=self.m.frame,event=event,detail=description)
        self.events.append(obj)
        print(self.case, obj,flush=True)
    def wait(self,n,reason):
        if n<0:raise ValueError('negative frame count')
        for _ in range(n):self.m.run_frame()
        self.log('wait',f'{n} frames: {reason}')
    def tap(self,keys,hold=4,release=9):
        if isinstance(keys,str):keys=(keys,)
        self.log('press',f'{"+".join(keys)} (hold {hold}, release {release})')
        self.m.press(keys)
        for _ in range(hold):self.m.run_frame()
        self.m.press(())
        for _ in range(release):self.m.run_frame()
    def key(self,key,hold=4,release=9):self.tap((key,),hold,release)
    def text(self,txt):
        for ch in txt:
            if ch=='\n':self.key('ENTER')
            elif ch==' ':self.key('SPACE')
            elif ch=='"':self.tap(('SS','p'))
            elif ch=='.':self.tap(('SS','m'))
            elif ch==',':self.tap(('SS','n'))
            elif ch==':':self.tap(('SS','z'))
            elif ch=='-':self.tap(('SS','j'))
            elif ch=='*':self.tap(('SS','b'))
            elif ch.isupper():self.tap(('CS',ch.lower()))
            elif ch.islower() or ch.isdigit():self.key(ch)
            else:raise ValueError(f'unhandled key {ch!r}')
    def load(self,name):
        tape=FILES[name].read_bytes()
        blocks=list(CONV.tzx_blocks(tape))
        assert len(blocks)==2 and blocks[0][0]==0 and blocks[1][0]==255
        self.m.cassette=blocks.copy()
        for keys in [('j',),('SS','p'),('SS','p'),('ENTER',)]:self.tap(keys)
        self.wait(70,'ROM tape loading completion')
        m=self.m.mem
        w=lambda a:m[a]|(m[a+1]<<8)
        prog,vars=w(0x5c53),w(0x5c4b)
        n=int.from_bytes(blocks[0][16:18],'little')
        expected=blocks[1][1:1+n];actual=bytes(m[prog:vars])
        ok=expected==actual
        self.log('load',f'{name} {len(actual)} numbered BASIC bytes exact={ok}; {len(self.m.cassette)} blocks remain')
        self.load_details.append(dict(name=name,frame=self.m.frame,bytes=len(actual),identical=ok))
        if not ok:raise RuntimeError('tape load did not match source')
    def run(self):self.key('r');self.key('ENTER')
    def run_at(self,line):
        self.key('r');self.text(str(line)+'\n')
    def merge(self,name):
        blocks=list(CONV.tzx_blocks(FILES[name].read_bytes()))
        self.m.cassette=blocks.copy()
        self.tap(('CS','SS'))   # ENTER EXTENDED (E) mode
        self.tap(('SS','t'))    # MERGE token, extended + symbol shift + T
        self.tap(('SS','p'))    # first double quote
        self.tap(('SS','p'))    # closing double quote
        self.key('ENTER')
        self.wait(90, 'MERGE recorder into current BASIC program')
        self.log('merge',f'{name}: remaining recorded blocks={len(self.m.cassette)}')
    def raw_cmd(self,word,numeric=None):
        # Sinclair keyword mode single-key commands. Not arbitrary pasted source.
        if word=='RUN':self.run()
        elif word=='LIST':
            self.key('k')
            if numeric is not None:self.text(str(numeric))
            self.key('ENTER')
        else:raise ValueError(word)
    def dump(self):
        # Decode screen's 8x8 character cells by matching Sinclair ROM glyphs.
        # Only whole-cell chars are trusted; UDG sprites/overprints show as ?.
        mem=self.m.mem
        glyph={tuple(mem[0x3D00+(c-32)*8:0x3D00+(c-31)*8]):chr(c) for c in range(32,128)}
        rows=[]
        for cy in range(24):
            line=''
            for cx in range(32):
                bits=tuple(mem[0x4000 | ((((cy*8+i)&0xC0)<<5)) | (((cy*8+i)&7)<<8) | ((((cy*8+i)&0x38)<<2)) | cx] for i in range(8))
                ch=glyph.get(bits)
                if ch is None:ch=glyph.get(tuple(x^255 for x in bits))
                line+=ch or '?'
            rows.append(line.rstrip())
        return '\n'.join(f'{i:02d}| {r}' for i,r in enumerate(rows) if r.strip() or '?' in r)
    def screen(self,name):
        path=self.dir/(name+'.png')
        write_png(self.m.screen(),str(path),border=self.m.border,scale=2)
        text=self.dump()
        (self.dir/(name+'.txt')).write_text(text+'\n')
        self.captures.append(dict(name=name,frame=self.m.frame,screen=text))
        self.log('screen',name)
        print('===== SCREEN '+self.case+' '+name+' =====\n'+text+'\n========',flush=True)
    def save(self):
        (self.dir/'session.json').write_text(json.dumps(dict(program=self.case,events=self.events,loaded=self.load_details,captures=self.captures),indent=2,ensure_ascii=False)+'\n')

# Each pair of inputs and snapshots is an actual human keyboard path, not a
# simulated BASIC variable edit.  4/9 means 4 frames held + 9 released.
PLAN={
 'advent':[('text','take brass lamp\n'),('wait',430),('shot','after-take-lamp'),('text','inventory\n'),('wait',440),('shot','inventory'),('text','north\n'),('wait',430),('shot','kitchen')],
 'alienblitz':[('key','c',80),('wait',70),('shot','right'),('key','m',90),('wait',150),('shot','fire'),('key','x',70),('wait',100),('shot','left')],
 'asteroids':[('key','SPACE',18),('wait',120),('shot','restarted'),('key','8',65),('wait',80),('shot','steering-or-crash')],
 'blackjack':[('text','10\n'),('wait',550),('shot','cards-and-choice'),('text','n\n'),('wait',1050),('shot','settlement-or-next-hand')],
 'bubble':[('key','n',35),('wait',460),('shot','random-sort-in-progress'),('wait',1950),('shot','sort-complete-or-progress'),('key','n',25),('wait',100),('shot','quit-after-sort')],
 'chess':[('wait',380),('shot','human-move-prompt'),('text','e2'),('wait',100),('shot','from-e2'),('text','e4'),('wait',2400),('shot','after-e2-e4')],
 'clock':[('text','12\n'),('wait',80),('shot','minute-prompt'),('text','34\n'),('wait',70),('text','0\n'),('wait',130),('shot','alarm-prompt'),('text','n\n'),('wait',420),('shot','clock-running')],
 'delete':[('text','100\n'),('wait',90),('shot','end-line-prompt'),('text','110\n'),('wait',180),('shot','delete-prepared'),('text','100\n'),('wait',120),('shot','deleted-from-BASIC')],
 'draughts':[('wait',350),('shot','move-prompt'),('text','c6'),('wait',60),('shot','chosen-piece'),('text','d5'),('wait',420),('shot','after-move')],
 'eliminator':[('key','w',70),('wait',120),('shot','after-up'),('key','p',70),('wait',130),('shot','after-fire')],
 'equation':[('text','1\n'),('wait',40),('text','1\n'),('wait',40),('text','-5\n'),('wait',40),('text','2\n'),('wait',40),('text','-1\n'),('wait',40),('text','-1\n'),('wait',380),('shot','solved-or-plotting'),('text','n\n'),('wait',150),('shot','exit')],
 'escape':[('key','w',80),('wait',100),('shot','after-thrust'),('key','d',80),('wait',110),('shot','after-right')],
 'evaluate':[('text','HOME\n'),('wait',50),('text','2026\n'),('wait',45),('text','3\n'),('wait',45),('text','1\n'),('wait',140),('shot','item-entry'),('text','CAMERA\n'),('wait',45),('text','OFFICE\n'),('wait',45),('text','2022\n'),('wait',45),('text','5\n'),('wait',45),('text','100\n'),('wait',140),('shot','item-value'),('key','SPACE',20),('wait',150),('shot','summary-or-next'),('combo',('SS','b'),25),('wait',110),('shot','finished')],
 'geometry':[('text','0\n'),('wait',140),('shot','answer-feedback'),('text','\n'),('wait',120),('shot','next-question')],
 'hires':[('key','a',22),('wait',90),('shot','number-of-characters'),('key','1',22),('wait',190),('shot','character-editor'),('key','1',45),('wait',80),('shot','pixel-set'),('key','s',40),('wait',90),('shot','save-prompt'),('key','y',30),('wait',220),('shot','saved-graphics'),('key','n',30),('wait',250),('shot','another-character-prompt')],
 'invaders':[('key','c',90),('wait',85),('shot','move-right'),('key','m',95),('wait',120),('shot','missile')],
 'kings':[('key','1',30),('wait',110),('shot','answer-feedback'),('key','SPACE',35),('wait',120),('shot','next-question')],
 'lunar':[('key','7',65),('wait',140),('shot','thrust'),('key','5',65),('wait',160),('shot','left-or-landing')],
 'mazeman':[('key','SPACE',30),('wait',170),('shot','advance'),('key','o',35),('wait',180),('shot','turn-left'),('key','SPACE',30),('wait',160),('shot','advance-again')],
 'meteor':[('wait',1500),('shot','ready-after-countdown'),('key','p',65),('wait',90),('shot','right'),('key','w',65),('wait',90),('shot','up'),('key','0',55),('wait',130),('shot','weapon-or-game')],
 'monitor':[('text','16384\n'),('wait',120),('shot','screen-memory-hex'),('combo',('CS','8'),15),('wait',80),('shot','cursor-right'),('combo',('CS','6'),15),('wait',80),('shot','cursor-down')],
 'payroll':[('key','e',28),('wait',80),('shot','number-of-employees'),('text','1\n'),('wait',90),('shot','employee-name'),('text','ADA\n'),('wait',75),('text','10\n'),('wait',85),('shot','overtime-factor'),('text','1.5\n'),('wait',90),('shot','save-choice'),('text','no\n'),('wait',110),('shot','hour-entry'),('text','40\n'),('wait',80),('text','2\n'),('wait',140),('shot','wage-summary')],
 'renum':[('text','100\n'),('wait',40),('text','260\n'),('wait',40),('text','500\n'),('wait',40),('text','10\n'),('wait',480),('shot','renumber-complete'),('text','*\n'),('wait',170),('shot','exit-choice'),('text','n\n'),('wait',120),('shot','stopped'),('cmd','LIST',500),('wait',120),('shot','renumbered-list')],
 'sales':[('text','2024\n'),('wait',75),('shot','to-year'),('text','2025\n'),('wait',100),('shot','q1-prompt'),('text','100\n'),('wait',40),('text','200\n'),('wait',40),('text','300\n'),('wait',40),('text','400\n'),('wait',50),('text','300\n'),('wait',40),('text','400\n'),('wait',40),('text','500\n'),('wait',40),('text','600\n'),('wait',140),('shot','year-summary'),('text','n\n'),('wait',300),('shot','ratios'),('text','n\n'),('wait',320),('shot','graph')],
}

def run_case(case):
    s=Session(case)
    if case in ('delete','renum'):
        s.load('geometry')                 # real numbered BASIC lines to operate on
        s.merge(case)                      # ROM MERGE; no raw-memory insertion
        s.screen('merged-program-ready')
        s.run_at(9973 if case=='delete' else 9900)
    elif case=='f-way-frog':
        s.load('frogshapes');s.run();s.wait(950,'graphics preset concludes');s.screen('graphics-ready')
        s.load('f-way-frog');s.run()
    else:
        s.load(case);s.run()
    s.wait(450,'initial application state after RUN')
    s.screen('start')
    for step in PLAN.get(case,[]):
        kind=step[0]
        if kind=='text':s.text(step[1])
        elif kind=='key':s.key(step[1],hold=step[2],release=12)
        elif kind=='combo':s.tap(step[1],hold=step[2],release=12)
        elif kind=='wait':s.wait(step[1],'allow Spectrum BASIC to process inputs')
        elif kind=='shot':s.screen(step[1])
        elif kind=='cmd':s.raw_cmd(step[1],numeric=step[2])
        else:raise ValueError(step)
    s.save()
    return s

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--case',choices=sorted(FILES))
    p.add_argument('--intro-all',action='store_true')
    args=p.parse_args()
    if args.case:run_case(args.case)
    elif args.intro_all:
        for c in sorted(FILES):
            if c not in ('fruit','leapfrog','reversal','frogshapes','f-way-frog'):
                run_case(c)
    else:p.error('pass --case or --intro-all')
