#!/usr/bin/env python3
"""Run MCODER III against the 24 unmodified standalone OTS program tapes.

Uses original 48K ROM keyboard LOAD, LOAD "" CODE, and GO TO; ROM SAVE,
independent ROM LOAD and scripted human inputs. Writes only current compiled
trial deliverables and truthful status into the per-program folder. The emulator
fast-tape trap accelerates tape transfer only. Keep tape source bytes untouched.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import re
from mcoder3_experiment import (SpectrumSession,ROOT,ELIGIBLE,FILES,blocks_from_file,
                                first_line,tzx_from_blocks)
def screen_text(m):
    """Recognize complete 8x8 ROM glyphs only; graphics become '?' (not OCR)."""
    glyph={tuple(m.mem[0x3d00+(c-32)*8:0x3d00+(c-31)*8]):chr(c) for c in range(32,128)}
    lines=[]
    for cy in range(24):
        row=''
        for cx in range(32):
            bits=tuple(m.mem[0x4000|((((cy*8+i)&0xc0)<<5))|(((cy*8+i)&7)<<8)|((((cy*8+i)&0x38)<<2))|cx] for i in range(8))
            row+=glyph.get(bits,'?')
        if row.strip():lines.append(f'{cy:02d}| {row.rstrip()}')
    return '\n'.join(lines)
from walk_ots_all import PLAN

COMPILER=ROOT/'tools'/'MCODER-III-Compiler'/'M Coder 3.tzx'

def text_keys(s,txt):
    for c in txt:
        if c=='\n':s.key('ENTER')
        elif c==' ':s.key('SPACE')
        elif c=='"':s.key(('SS','p'))
        elif c=='.':s.key(('SS','m'))
        elif c==',':s.key(('SS','n'))
        elif c==':':s.key(('SS','z'))
        elif c=='-':s.key(('SS','j'))
        elif c=='*':s.key(('SS','b'))
        elif c.isupper():s.key(('CS',c.lower()))
        elif c.islower() or c.isdigit():s.key(c)
        else:raise ValueError(f'Unsupported human key: {c!r}')

def replay(s,case,out):
    if case=='fruit':steps=[('key','ENTER',4),('wait',350),('shot','first-spin'),('wait',700),('shot','later-spin')]
    elif case=='leapfrog':steps=[('text','45\n'),('wait',220),('shot','after-45'),('text','64\n'),('wait',220),('shot','after-64')]
    elif case=='reversal':steps=[('text','3\n'),('wait',280),('shot','after-3'),('text','0\n'),('wait',160),('shot','stopped')]
    elif case=='f-way-frog':steps=[('key','q',80),('wait',160),('shot','after-up'),('key','p',80),('wait',160),('shot','after-right')]
    elif case=='meteor':
        # MCODER executes rapidly: the original 1500-frame idle period let all
        # three lives expire before any control could be tried. Keep the same
        # actual held keys, but shorten only the initial human reaction delay.
        steps=[('wait',350),('shot','ready-earlier'),('key','p',65),('wait',90),
               ('shot','right'),('key','w',65),('wait',90),('shot','up'),
               ('key','0',55),('wait',130),('shot','weapon-or-game')]
    else:steps=PLAN.get(case,[])
    observations=[]
    for step in steps:
        kind=step[0]
        if kind=='text':text_keys(s,step[1])
        elif kind=='key':s.key(step[1],held=step[2],gap=12)
        elif kind=='combo':s.key(step[1],held=step[2],gap=12)
        elif kind=='wait':s.wait(step[1],'follow original human walkthrough pacing')
        elif kind=='shot':
            s.capture(out/('compiled-'+step[1]+'.png'))
            observations.append((step[1],screen_text(s.machine).splitlines()[-8:]))
        else:raise ValueError(step)
    return observations

def attempt(case,max_frames,replay_keys):
    out=FILES[case].parent
    tape=out/(case+'-mcoder3.tzx')
    statusfile=out/'compiled-test.md'
    source=SpectrumSession()
    if case=='f-way-frog':
        source.load_basic('frogshapes');source.key('r');source.key('ENTER');source.wait(950,'initializing UDGs from original frogshapes')
    source.load_basic(case)
    before=source.program(case)
    source.load_code(blocks_from_file(COMPILER))
    compiler_state='NOT COMPLETE'
    lastline=''
    elapsed=0
    while elapsed<max_frames:
        n=min(120,max_frames-elapsed)
        source.wait(n,'real MCODER compilation')
        elapsed+=n
        screen=screen_text(source.machine)
        lastline=screen.splitlines()[-1] if screen else ''
        # A ROM error on the compiler screen is a terminal *observed* result,
        # unlike a temporary progress number or an unfinished tape.
        error_rows = [line for line in screen.splitlines()
                      if re.search(r'\b[1-9] (?:Subscript wrong|Out of memory|Invalid argument|Variable not found|Integer out of range|Nonsense in BASIC|Number too big|RETURN without GOSUB|Out of DATA)\b', line)]
        if error_rows:
            compiler_state='FAILED (observed ROM error)'
            lastline=error_rows[-1]
            break
        if not source.machine.cassette and '0 OK' in lastline and source.program(case)!=before:
            compiler_state='COMPLETED'
            break
    after=source.program(case)
    source.capture(out/'compiler-status.png')
    note=[f'# {case} — MCODER III compilation', '',
          'Original source is preserved. Compiler loaded from its unchanged TZX through real Sinclair ROM LOAD "" CODE.',
          f'Compiler observed: **{compiler_state}** (waited {elapsed} emulated 50 Hz frames).',
          f'BASIC source bytes: {len(before)}; memory bytes after compiler: {len(after)}; '
          f'compiler tape blocks remaining: {len(source.machine.cassette)}.',
          f'Last visible compiler screen row: `{lastline}`.', '']
    result={'program':case,'compiler':compiler_state,'source_bytes':len(before),
            'post_bytes':len(after),'blocks_remaining':len(source.machine.cassette),'frames':elapsed,
            'lastline':lastline,'fresh_load':False,'startup':False,'replayed':False}
    if compiler_state!='COMPLETED':
        if compiler_state.startswith('FAILED'):
            note.append('Compilation halted at the observed Sinclair ROM error above. No compiled TZX created. The root cause is not established; original source is unchanged.')
        else:
            note.append('No compiled TZX: compiler completion was not verified at this frame limit. This is NOT a compiler-error diagnosis.')
        statusfile.write_text('\n'.join(note)+'\n')
        return result
    try:
        saved=source.save_basic('MC')
        tape.write_bytes(tzx_from_blocks(saved))
        fresh=SpectrumSession()
        if case=='f-way-frog':
            fresh.load_basic('frogshapes');fresh.key('r');fresh.key('ENTER');fresh.wait(950,'graphics initializer on new Spectrum')
        fresh.machine.cassette=blocks_from_file(tape)
        for k in ['j',('SS','p'),('SS','p'),'ENTER']:fresh.key(k)
        fresh.wait(130,'fresh ROM LOAD')
        result['fresh_load']=not fresh.machine.cassette
        if not result['fresh_load']:raise RuntimeError('Standalone compiled LOAD left cassette blocks')
        line=first_line(case)
        fresh.goto(line)
        fresh.wait(450,'compiled program initial execution')
        fresh.capture(out/'compiled-start.png')
        start_screen=screen_text(fresh.machine)
        startup_errors=[row for row in start_screen.splitlines()
                        if 'RAMTOP no good' in row or re.search(r'\b[1-9] (?:Subscript wrong|Out of memory|Invalid argument|Variable not found|Integer out of range|Nonsense in BASIC|Number too big|RETURN without GOSUB|Out of DATA)\b',row)]
        if startup_errors:
            result['startup_error']=startup_errors[-1]
            raise RuntimeError('Compiled tape loaded but GO TO caused ROM error: '+startup_errors[-1])
        result['startup']=True
        note.extend([f'ROM SAVE produced a compiled BASIC TZX. Fresh Spectrum loaded it without the compiler: **yes**.',
                     f'Ran `GO TO {line}`. Compiled start screenshot: `compiled-start.png`.',
                     f'Start screen final rows: `{screen_text(fresh.machine).splitlines()[-3:]}`.', ''])
        if replay_keys:
            observations=replay(fresh,case,out)
            result['replayed']=bool(observations)
            note.extend(['Replayed the previously recorded human-keyboard sequence, with its actual key holds/releases.',
                         'Observed screenshot labels and last screen rows:'])
            note.extend([f'- `{label}`: `{lines}`' for label,lines in observations])
            note.extend(['', 'Parity is **not yet confirmed** solely from this automated sequence; compare saved screenshots to original walkthrough and account for random outcomes.'])
        else:
            note.append('Human walkthrough comparison pending. The compiled-start screenshot is not sufficient to claim parity.')
        note.append('No win or exhaustive compatibility claimed.')
    except Exception as exc:
        result['error']=type(exc).__name__+': '+str(exc)
        note.extend([f'Fresh SAVE/LOAD/RUN or replay failed: {result["error"]}',
                     'Do not count an independently running compiled tape unless the fresh ROM test succeeded.'])
    statusfile.write_text('\n'.join(note)+'\n')
    return result


def verify_saved(case,replay_keys):
    """Only fresh-load/replay an already ROM-saved compiled TZX; do not recompile."""
    out=FILES[case].parent
    tape=out/(case+'-mcoder3.tzx')
    if not tape.is_file():raise FileNotFoundError(tape)
    fresh=SpectrumSession()
    if case=='f-way-frog':
        fresh.load_basic('frogshapes');fresh.key('r');fresh.key('ENTER');fresh.wait(950,'UDG initializer')
    fresh.machine.cassette=blocks_from_file(tape)
    for k in ['j',('SS','p'),('SS','p'),'ENTER']:fresh.key(k)
    fresh.wait(130,'fresh ROM LOAD of saved compiled tape')
    if fresh.machine.cassette:raise RuntimeError('Fresh ROM did not finish loading saved tape')
    first=first_line(case)
    fresh.goto(first)
    fresh.wait(450,'compiled program startup')
    fresh.capture(out/'compiled-start.png')
    ss=screen_text(fresh.machine)
    snaps=replay(fresh,case,out) if replay_keys else []
    statusfile=out/'compiled-test.md'
    text=[f'# {case} — MCODER III compilation', '',
          'Compiled tape was produced from original BASIC with real ROM MCODER and then saved with ROM SAVE. This verifies the previously saved tape only, without repeating the compiler run.',
          'Fresh Sinclair ROM LOAD without compiler: **yes**.',
          f'Executed `GO TO {first}`.',f'Start display last rows: `{ss.splitlines()[-8:]}`.',
          'Original-source human keyboard sequence replayed: '+str(bool(snaps))+'.',
          'Visible result snapshots:']
    text.extend([f'- `{name}`: `{rows}`' for name,rows in snaps])
    text.extend(['', 'Human parity requires reviewing screenshots against the existing original walkthrough. No exhaustive compatibility claim.'])
    statusfile.write_text('\n'.join(text)+'\n')
    return {'program':case,'compiler':'COMPLETED (previously saved)','fresh_load':True,'startup':True,'replayed':bool(snaps),'first_line':first}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--program',action='append',choices=ELIGIBLE)
    ap.add_argument('--max-frames',type=int,default=2500)
    ap.add_argument('--replay',action='store_true')
    ap.add_argument('--verify-saved',action='store_true',help='resume fresh ROM LOAD from already saved compiled TZX')
    args=ap.parse_args()
    assert COMPILER.is_file(),COMPILER
    results=[]
    for case in (args.program or ELIGIBLE):
        print('START',case,flush=True)
        try:result=verify_saved(case,args.replay) if args.verify_saved else attempt(case,args.max_frames,args.replay)
        except Exception as exc:result={'program':case,'error':type(exc).__name__+': '+str(exc)}
        results.append(result)
        print('RESULT',json.dumps(result),flush=True)
    print('TOTAL',len(results),'observed compilation complete',sum(x.get('compiler')=='COMPLETED' for x in results),
          'fresh reloads',sum(x.get('fresh_load') for x in results),flush=True)
if __name__=='__main__':main()
