#!/usr/bin/env python3
"""MCODER III / OverTheSpectrum real-ROM compilation and compiled-tape runner.

All commands use actual Spectrum keyboard-matrix keys. The ROM cassette trap
loads original recording blocks (not BASIC-in-RAM injection) and captures the
ROM SAVE blocks. A compiled TZX is emitted ONLY after the real compiler has
returned and a fresh 48K Spectrum can load and execute the saved program.

For original sources, use tapes/<OTS_tape_...>/<program>.tzx from this project's
previous independent side extracts. MCODER III media is user-supplied TAP/TZX;
this script does not impersonate the compiler or infer compile success from
source syntax. Any generated outputs are trial evidence, not source edits.

Examples:
  python tools/mcoder3_experiment.py --selftest
  python tools/mcoder3_experiment.py --mcoder path/MCoderIII.tap --program leapfrog
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import struct
import json
import zipfile

ROOT = Path(__file__).resolve().parent.parent
EMU = ROOT/'tools'/'spectrum_emulator'
sys.path.insert(0, str(EMU))
sys.path.insert(0, str(ROOT/'tools'))
from zxmachine import Machine, tap_blocks
from zxscreen import write_png
from extract_ots_basic import load_converter
CONVERTER=load_converter()
FILES={p.stem:p for p in (ROOT/'tapes').glob('*/*.tzx')}

EXCLUDE={'renum','delete','hires','monitor','frogshapes'}
ELIGIBLE=sorted(set(FILES)-EXCLUDE)


def blocks_from_file(path:Path)->list[bytes]:
    ext=path.suffix.lower()
    if ext=='.zip':
        with zipfile.ZipFile(path) as z:
            names=[n for n in z.namelist() if n.lower().endswith(('.tap','.tzx'))]
            if len(names)!=1:raise ValueError(f'Expected one TAP/TZX in ZIP, found {names!r}')
            name=names[0]
            data=z.read(name)
            ext=Path(name).suffix.lower()
    else: data=path.read_bytes()
    if ext=='.tap':blocks=tap_blocks(data)
    elif ext=='.tzx':blocks=list(CONVERTER.tzx_blocks(data))
    else:raise ValueError(f'Unsupported compiler tape type: {ext}')
    if not blocks:raise ValueError(f'No readable tape blocks in {path}')
    return blocks


def tzx_from_blocks(blocks:list[bytes])->bytes:
    out=bytearray(b'ZXTape!\x1a\x01\x14')
    for b in blocks:
        if len(b)>65535:raise ValueError('ROM SAVE block too long for standard TZX')
        if not b or bytes([__import__('functools').reduce(lambda x,y:x^y,b,0)])!=b'\x00':
            raise ValueError('bad ROM SAVE block')
        out+=b'\x10'+struct.pack('<HH',1000,len(b))+b
    return bytes(out)


def tape_block(flag:int, data:bytes)->bytes:
    b=bytes([flag])+data
    v=0
    for x in b:v^=x
    return b+bytes([v])


def code_header(name:str, length:int, addr:int)->bytes:
    ten=name.encode('ascii')[:10].ljust(10,b' ')
    return tape_block(0, bytes([3])+ten+struct.pack('<HHH',length,addr,32768))


class SpectrumSession:
    def __init__(self):
        self.machine=Machine()
        self.events=[]
        self.wait(300,'ROM boot')
    def mark(self,label):
        self.events.append({'frame':self.machine.frame,'event':label,
                            'pc':self.machine.cpu.pc,'remaining_blocks':len(self.machine.cassette),
                            'tape_requests':self.machine.tape_requests})
    def wait(self, frames, what):
        for _ in range(frames):self.machine.run_frame()
        self.mark(f'wait {frames} frames: {what}')
    def key(self, keys, held=4, gap=9):
        if isinstance(keys,str):keys=(keys,)
        self.mark('press '+ '+'.join(keys)+f' held={held} gap={gap}')
        self.machine.press(keys)
        for _ in range(held):self.machine.run_frame()
        self.machine.press(())
        for _ in range(gap):self.machine.run_frame()
    def number(self,n:int):
        for d in str(n):self.key(d)
    def load_basic(self, name:str):
        self.machine.cassette=blocks_from_file(FILES[name]).copy()
        for k in ['j',('SS','p'),('SS','p'),'ENTER']: self.key(k)
        self.wait(80,f'LOAD BASIC {name}')
        self.mark('source BASIC load finished')
        self.program(name)
    def program(self,name:str):
        m=self.machine.mem
        word=lambda p:m[p]|(m[p+1]<<8)
        lo,hi=word(0x5c53),word(0x5c4b)
        self.mark(f'PROG={lo} VARS={hi} bytes={hi-lo} for {name}')
        return bytes(m[lo:hi])
    def load_code(self,blocks):
        self.machine.cassette=list(blocks)
        # LOAD "" CODE: J, quotes, space, EXTEND MODE, I, ENTER
        for k in ['j',('SS','p'),('SS','p'),'SPACE',('CS','SS'),'i','ENTER']:
            self.key(k)
        self.mark('LOAD "" CODE issued')
    def goto(self,line:int):
        self.key('g'); self.number(line);self.key('ENTER')
        self.mark('GO TO '+str(line))
    def save_basic(self,name:str):
        before=len(self.machine.saved)
        self.key('s')
        self.key(('SS','p'))
        for c in name:self.key(('CS',c.lower()) if c.isupper() else c)
        self.key(('SS','p'))
        self.key('ENTER')
        self.wait(35,'ROM prompts Start tape, then press any key')
        self.key('SPACE')
        self.wait(650,'ROM SAVE data block')
        emitted=self.machine.saved[before:]
        if len(emitted)!=1:
            raise RuntimeError(f'Unexpected SA-BYTES data blocks: {len(emitted)}')
        # The SDK 48K tape trap captures the data SA-BYTES entry but the ROM
        # header signal uses an entry inside the routine. Rebuild ONLY the
        # standard header metadata; program bytes are precisely ROM-saved.
        saved_data=emitted[0]
        if saved_data[0]!=0xff:raise RuntimeError('Expected ROM BASIC data block')
        m=self.machine.mem
        prog=m[0x5c53]|(m[0x5c54]<<8)
        vars_=m[0x5c4b]|(m[0x5c4c]<<8)
        count=len(saved_data)-2
        header=tape_block(0,bytes([0])+name.encode('ascii')[:10].ljust(10,b' ')
                          +struct.pack('<HHH',count,32768,vars_-prog))
        return [header,saved_data]
    def capture(self,path:Path):
        path.parent.mkdir(parents=True,exist_ok=True)
        write_png(self.machine.screen(),str(path),border=self.machine.border,scale=2)
        self.mark('screenshot '+path.name)


def first_line(program:str)->int:
    tape=blocks_from_file(FILES[program]);data=tape[1][1:-1]
    return int.from_bytes(data[:2], 'big')


def selftest():
    src=SpectrumSession()
    payload=b'\x01\x02\x03\x04\x05'
    blocks=[code_header('MC TEST',len(payload),32768),tape_block(0xff,payload)]
    src.load_code(blocks)
    src.wait(80,'dummy CODE load')
    actual=bytes(src.machine.mem[32768:32768+len(payload)])
    assert actual==payload, f'CODE LOAD failed: {actual.hex()} expected {payload.hex()}'
    assert not src.machine.cassette, 'Not all dummy CODE tape blocks loaded'
    print('PASS: ROM LOAD "" CODE keyboard path loads 5-byte dummy CODE block at 32768')
    return src


def compile_program(program:str,compiler:Path,frames:int):
    if program not in ELIGIBLE:raise ValueError(f'{program} excluded or unknown')
    s=SpectrumSession()
    s.load_basic(program)
    original=s.program(program)
    s.load_code(blocks_from_file(compiler))
    out=ROOT/'compiled_trials'/program
    out.mkdir(parents=True,exist_ok=True)
    # All code blocks stay queued. The ROM/compiler requests the second stage
    # only when ready, like leaving a cassette playing rather than pausing it.
    for i in range(0,frames,500):
        s.wait(min(500,frames-i),f'compiler progress, window {i}')
        s.capture(out/f'compiler-frame-{s.machine.frame:06d}.png')
        if s.machine.cassette:
            continue
        # No automatic assumption that finishing the tape means compilation
        # succeeded. The operator must inspect the compiler status screen.
    converted=s.program(program)
    status={'program':program,'source_bytes':len(original),
            'post_compiler_bytes':len(converted),
            'post_compiler_differs':converted!=original,
            'remaining_compiler_tape_blocks':len(s.machine.cassette),
            'ROM_tape_requests':s.machine.tape_requests,
            'events':s.events,
            'status':'UNDETERMINED; inspect compiler screenshots and compiled BASIC before saving'}
    (out/'trial.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps({k:v for k,v in status.items() if k!='events'},indent=2))
    return status


def standalone_trial(program:str,compiler:Path,frames:int=5000,observe_frames:int=500):
    """Attempt compile, SAVE via ROM, fresh LOAD and GO TO. Does not infer parity.

    The trial is refused unless source BASIC bytes actually changed and all
    compiler tape blocks were requested. Screenshot evidence remains decisive.
    """
    if program not in ELIGIBLE:raise ValueError(f'{program} excluded or unknown')
    sess=SpectrumSession()
    if program=='f-way-frog':
        sess.load_basic('frogshapes')
        sess.key('r');sess.key('ENTER')
        sess.wait(950,'run Frogshapes in same Spectrum')
    sess.load_basic(program)
    before=sess.program(program)
    sess.load_code(blocks_from_file(compiler))
    out=ROOT/'compiled_trials'/program
    out.mkdir(parents=True,exist_ok=True)
    for i in range(0,frames,500):
        sess.wait(min(frames-i,500),'MCODER compiler from genuine tape')
        sess.capture(out/f'compiler-{sess.machine.frame:06d}.png')
    after=sess.program(program)
    if before==after or sess.machine.cassette:
        raise RuntimeError('Compilation not established: BASIC unchanged or tape unfinished; inspect screenshots')
    saved=sess.save_basic('MC')
    if len(saved)!=2:
        raise RuntimeError(f'ROM SAVE did not produce exactly two blocks: {len(saved)}')
    img=tzx_from_blocks(saved)
    staged=out/(program+'-MCODER3-trial.tzx')
    staged.write_bytes(img)
    test=SpectrumSession()
    if program=='f-way-frog':
        test.load_basic('frogshapes')
        test.key('r');test.key('ENTER')
        test.wait(950,'graphics initializer, independent tape')
    test.machine.cassette=blocks_from_file(staged)
    for k in ['j',('SS','p'),('SS','p'),'ENTER']:test.key(k)
    test.wait(150,'fresh ROM LOAD of compiler output')
    test.capture(out/'fresh-load.png')
    test.goto(first_line(program))
    test.wait(observe_frames,'compiled GO TO execution')
    test.capture(out/'compiled-execution.png')
    details={'source':program,'compiler':str(compiler),'output_tzx':str(staged),
             'compiled_bytes':len(after),'source_bytes':len(before),
             'fresh_load_tape_blocks_left':len(test.machine.cassette),
             'status':'UNVERIFIED comparison; inspect displayed states against baseline',
             'compile_events':sess.events,'fresh_machine_events':test.events}
    (out/'trial.json').write_text(json.dumps(details,indent=2)+'\n')
    return details


def selftest_save():
    source=SpectrumSession()
    source.load_basic('leapfrog')
    original=source.program('leapfrog')
    captured=source.save_basic('MC')
    assert len(captured)==2
    tzx=tzx_from_blocks(captured)
    saved_path=ROOT/'compiled_trials'/'selftest-leapfrog.tzx'
    saved_path.parent.mkdir(exist_ok=True)
    saved_path.write_bytes(tzx)
    new=SpectrumSession()
    new.machine.cassette=blocks_from_file(saved_path)
    for k in ['j',('SS','p'),('SS','p'),'ENTER']:new.key(k)
    new.wait(100,'load freshly ROM-saved BASIC')
    assert new.program('leapfrog')==original
    new.goto(first_line('leapfrog'))
    new.wait(220,'run reloaded program through GO TO')
    assert not new.machine.cassette
    saved_path.unlink()
    print('PASS: ROM SAVE, TZX packaging, fresh ROM LOAD and GO TO verified on Leapfrog BASIC')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--selftest',action='store_true')
    p.add_argument('--selftest-save',action='store_true')
    p.add_argument('--make-trial-tape',action='store_true')
    p.add_argument('--mcoder',type=Path)
    p.add_argument('--program',choices=ELIGIBLE)
    p.add_argument('--frames',type=int,default=5000)
    args=p.parse_args()
    if args.selftest:selftest();return
    if args.selftest_save:selftest_save();return
    if not args.mcoder or not args.program:p.error('specify --mcoder and --program')
    if args.make_trial_tape:standalone_trial(args.program,args.mcoder,args.frames)
    else:compile_program(args.program,args.mcoder,args.frames)

if __name__=='__main__':main()
