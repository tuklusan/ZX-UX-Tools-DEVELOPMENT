#!/usr/bin/env python3
"""Run Sinclair ROM tape in Fuse and demand runtime ZX Printer completion marker."""
import os, pathlib, subprocess, sys, time
name=sys.argv[1]
root=pathlib.Path(__file__).resolve().parent
work=root/'fuse-artifacts'/name
work.mkdir(parents=True,exist_ok=True)
tape=root/'ci-tapes'/f'{name}.tap'
assert tape.exists(),tape
printer=work/'printer.txt'
images=work/'printer.pbm'
log=work/'fuse.log'
rom=os.environ.get('FUSE_ROM','')
assert pathlib.Path(rom).is_file(),f'No 48K ROM file: {rom!r}'
cmd=['fuse','--machine','48','--rom-48',rom,'--auto-load','--accelerate-loader','--speed','1000','--zxprinter','--textfile',str(printer),'--graphicsfile',str(images),'--no-confirm-actions','--tape',str(tape)]
print('Launching Fuse:', ' '.join(cmd),flush=True)
expected=f'DONE {name[:10]}'
passed=False
last=''
with log.open('wb') as fp:
    proc=subprocess.Popen(cmd,stdout=fp,stderr=subprocess.STDOUT,env={**os.environ,'SDL_AUDIODRIVER':'dummy'})
    try:
        time.sleep(3)
        windows=subprocess.run(['xdotool','search','--name','Fuse'],capture_output=True,text=True).stdout.split()
        assert windows, 'Fuse SDL window not found'
        subprocess.run(['xdotool','windowfocus','--sync',windows[-1]],check=True)
        for keys in (['j'],['ctrl+p'],['ctrl+p'],['Return']):
            subprocess.run(['xdotool','key','--clearmodifiers',*keys],check=True)
            time.sleep(.22)
        print('Typed LOAD "" at the 48K ROM prompt',flush=True)
        deadline=time.monotonic()+int(os.environ.get('FUSE_TIMEOUT','250'))
        while time.monotonic()<deadline:
            if printer.exists():
                last=printer.read_text(encoding='latin1',errors='replace')
                if any(line.strip()==expected for line in last.splitlines()):
                    passed=True
                    break
            if proc.poll() is not None:
                print('Fuse exited:',proc.returncode,flush=True)
                break
            time.sleep(.6)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try: proc.wait(6)
            except subprocess.TimeoutExpired: proc.kill();proc.wait()
print('Printer tail:',repr(last[-1400:]),flush=True)
print('Fuse log:',log.read_text(encoding='utf-8',errors='replace')[-2000:],flush=True)
if not passed: sys.exit(f'FAIL {name}: runtime ROM LPRINT marker {expected!r} not found.')
print(f'PASS {name}: 48K Fuse ROM printer emitted {expected!r}',flush=True)
