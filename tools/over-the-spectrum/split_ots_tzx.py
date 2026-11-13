#!/usr/bin/env python3
"""Inspect and split OTS side tapes into one independently loadable TZX per BASIC header.

Preserves exact header/data TZX records and timing. Removes only side-level
metadata and tape-stop separators. A graphics setup BASIC (frogshapes) stays
its own separately loadable tape, never silently merged with the game.
Original side recordings and extracted BAS files remain untouched.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re

SIG=b'ZXTape!\x1a'

def get16(data,i): return int.from_bytes(data[i:i+2],'little')
def get24(data,i): return int.from_bytes(data[i:i+3],'little')
def get32(data,i): return int.from_bytes(data[i:i+4],'little')

def records(data):
    if not data.startswith(SIG) or len(data)<10: raise ValueError('Not a TZX file')
    pos=10
    while pos < len(data):
        start=pos; typ=data[pos];pos+=1
        meta=''
        if typ==0x10:
            size=get16(data,pos+2); pos+=4
            payload=data[pos:pos+size];pos+=size
        elif typ==0x11:
            size=get24(data,pos+15);pos+=18
            payload=data[pos:pos+size];pos+=size
        elif typ==0x14:
            size=get24(data,pos+7);pos+=10
            payload=data[pos:pos+size];pos+=size
        elif typ==0x20:
            meta=f'pause={get16(data,pos)}';pos+=2;payload=None
        elif typ in (0x21,0x30):
            size=data[pos];pos+=1
            meta=repr(data[pos:pos+size]);pos+=size;payload=None
        elif typ==0x22:payload=None
        elif typ==0x31:
            size=data[pos+1];pos+=2+size;payload=None
        elif typ in (0x28,0x32):
            size=get16(data,pos);pos+=2+size;payload=None
        elif typ==0x33:
            count=data[pos];pos+=1+3*count;payload=None
        elif typ==0x35:
            size=get32(data,pos+16);pos+=20+size;payload=None
        elif typ==0x5a:pos+=9;payload=None
        elif typ in (0x23,0x24,0x2a):pos+=2 if typ!=0x2a else 4;payload=None
        else: raise ValueError(f'Unknown TZX type 0x{typ:02x}, byte offset {start}')
        if pos>len(data):raise ValueError(f'Truncated record 0x{typ:02x} at {start}')
        kind='other';name='';subtype='';length=None
        if payload is not None:
            if len(payload)<2 or (not len(payload) and typ==0x10):raise ValueError('Empty data record')
            xor=0
            for b in payload:xor^=b
            if xor:raise ValueError(f'Failed TZX parity at {start}')
            kind=f'flag-{payload[0]:02x}'
            length=len(payload)-2
            if payload[0]==0 and len(payload)==19:
                kind='header';subtype=payload[1]
                name=payload[2:12].decode('latin1').strip()
                length=get16(payload,12)
                if subtype==0:meta=f'autostart={get16(payload,14)} vars={get16(payload,16)}'
                elif subtype==3:meta=f'load={get16(payload,14)}'
        yield dict(start=start,end=pos,raw=data[start:pos],type=typ,kind=kind,
                   name=name,subtype=subtype,length=length,meta=meta)

def inspect(path):
    data=path.read_bytes();rs=list(records(data))
    print(f'== {path.name}: {len(data)} bytes, {len(rs)} records ==')
    for i,r in enumerate(rs):
        bits=f'{i:2}  {r["type"]:02X} {r["kind"]:7}'
        if r['kind']=='header':bits+=f'  type={r["subtype"]} name={r["name"]!r:16} size={r["length"]}'
        if r['kind']=='flag-ff':bits+=f'  bytes={r["length"]}'
        if r['meta']:bits+=f'  {r["meta"]}'
        print(bits)

def split(path,out):
    tape=path.read_bytes()
    rs=list(records(tape))
    match=re.search(r'Cassette([123])_Side([AB])',path.name)
    if not match:raise ValueError(f'Unrecognized OTS tape file name: {path.name}')
    cassette,side=match.groups()
    entries=[]
    for n,r in enumerate(rs):
        if r['kind']!='header':continue
        if r['subtype']!=0:raise ValueError(f'Unexpected non-BASIC block: {r["name"]!r}')
        if n+1>=len(rs) or rs[n+1]['kind']!='flag-ff':
            raise ValueError(f'Unpaired BASIC header: {r["name"]!r}')
        d=rs[n+1]
        if d['length']!=r['length']:
            raise ValueError(f'Length mismatch for {r["name"]!r}')
        slug=re.sub('[^a-z0-9]+','-',r['name'].lower()).strip('-')
        if r['name'].lower()=="f'way frog":slug='f-way-frog'
        folder=out/f'OTS_tape_{cassette}_side_{side}_{slug}'
        target=folder/f'{slug}.tzx'
        contents=tape[:10]+r['raw']+d['raw']
        if target.exists():
            if target.read_bytes()!=contents:raise FileExistsError(target)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(contents)
        entries.append(target)
        print(f'Cassette {cassette}{side}  {r["name"]:12}  {target.relative_to(out)}  ({len(contents)} bytes)')
    return entries

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('files',nargs='+',type=Path)
    ap.add_argument('--out',type=Path)
    a=ap.parse_args()
    for f in a.files:
        if a.out:split(f,a.out)
        else:inspect(f)
