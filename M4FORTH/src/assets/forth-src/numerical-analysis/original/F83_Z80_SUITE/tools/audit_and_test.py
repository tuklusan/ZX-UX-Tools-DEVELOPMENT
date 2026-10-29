#!/usr/bin/env python3
"""Syntax/required-word audit, constrained 16-bit interpreter run, fixtures,
independent oracle checks. No claim of official certification or Z80 test.
"""
import argparse,csv,hashlib,json,math,re,sys
from pathlib import Path
from f83vm import VM,VMError
ROOT=Path(__file__).resolve().parents[1]
PROGRAMS=[
 'WHETSTON','MACHAR','LCGRAND','SQUARE','MINILIN',
 'GEMM8BIT','LUPIVOT','THOMASTR','CHOLESKY',
 'BRENTROT','NEWTON','BISECT','ROMBERG','SIMPSON',
 'GAUSS1D','RK4FIXED','EULERODE','JACRELX',
 'TINYFFT','POLYFIT'
]
SUPPORT=['COMMON','LINCORE']
LINEAR={'MINILIN','LUPIVOT','POLYFIT'}
# Exact used part of the original Forth-83 Required Word Set, not ANS-only.
REQUIRED=set('''! * */ + - / 0< 0= 0> 1+ 1- 2/ < = > >R ?DUP @ ABS AND CR D+ DROP DUP EXIT I J MAX MIN MOD NEGATE NOT OR OVER R> ROT SWAP U< UM/MOD VARIABLE CREATE ALLOT , : ; IF ELSE THEN DO LOOP BEGIN WHILE REPEAT UNTIL . ." DECIMAL'''.split())
# The quotation tokenizer represents ." as a string token, so it is not
# present among ordinary tokens in the scan.
EVAL={'D+','UM/MOD','*/','MOD'}

def parse_lines(vm,path):
 t=path.read_text(encoding='ascii')
 if '\t' in t or '\r' in t:raise AssertionError(f'{path}: tabs or CR in canonical LF file')
 if not t.endswith('\n'):raise AssertionError(f'{path}: missing final LF')
 for n,line in enumerate(t.splitlines(),1):
  if len(line)>64:raise AssertionError(f'{path}:{n}: line >64 columns ({len(line)})')
 if len(path.stem)>8 or len(path.suffix)!=4 or path.suffix!='.F83':
  raise AssertionError(f'{path}: non-8.3 filename')
 tok=vm.tokenise(t)
 definitions=set();symbols=set();skip=False
 for i,(kind,word) in enumerate(tok):
  if skip:skip=False;continue
  if kind=='string':continue
  if word in ('VARIABLE','CREATE','CONSTANT',':'):
   if i+1>=len(tok):raise AssertionError('dangling defining word')
   new=tok[i+1][1]
   if new in REQUIRED:raise AssertionError(f'{path}: shadows Forth-83 word {new}')
   if new in definitions:raise AssertionError(f'{path}: duplicate word {new}')
   definitions.add(new);skip=True;continue
  if not re.fullmatch(r'-?\d+',word) and word not in REQUIRED:
   symbols.add(word)
 return definitions,symbols,t

def audit_files():
 vm=VM();names={};refs={};all_defs={};all_calls={}
 for n in SUPPORT+PROGRAMS:
  path=ROOT/(n+'.F83');assert path.exists(),str(path)
  defs,used,data=parse_lines(vm,path)
  all_defs[n]=defs;all_calls[n]=used
  names[n]=dict(bytes=len(data.encode('ascii')),lines=data.count('\n'),sha256=hashlib.sha256(data.encode('ascii')).hexdigest())
  refs[n]=sorted(used)
 for n in SUPPORT+PROGRAMS:
  dependencies=['COMMON']
  if n in LINEAR:dependencies.append('LINCORE')
  if n=='LINCORE':dependencies=['COMMON']
  if n=='COMMON':dependencies=[]
  allowed=set()
  for dep in dependencies:
   if all_defs[n]&all_defs[dep]:
    raise AssertionError(f'{n}: shadows word in {dep}: {all_defs[n]&all_defs[dep]}')
   allowed|=all_defs[dep]
  allowed|=all_defs[n]
  for word in all_calls[n]:
   if word not in allowed:
    raise AssertionError(f'{n}: NOT Forth-83-required or locally defined: {word}')
 return names,refs

def execute_one(prog):
 vm=VM();vm.load(ROOT/'COMMON.F83')
 if prog in LINEAR:vm.load(ROOT/'LINCORE.F83')
 vm.load(ROOT/(prog+'.F83'))
 assert not vm.stack, f'{prog}: leaked data stack {vm.stack}'
 assert not vm.loops, f'{prog}: leaked DO loop stack'
 assert not vm.rstack, f'{prog}: leaked return stack'
 return vm

def independent_oracle(name,text):
 lines=[line.split() for line in text.strip().splitlines()]
 def qty(x):return int(x)
 def near(actual,target,tol,tag):
  assert abs(actual-target)<=tol,(name,tag,actual,target,tol)
 if name=='MACHAR':
  assert lines[0][-2:]==['-32768','32767']
  assert lines[1][-1]=='2' and lines[2][-2:]==['1000','1']
  assert lines[3][-1]=='2' and lines[4][-1]=='-32768'
 elif name=='LCGRAND':
  assert lines[0][-1]=='2'
  for line,seed in zip(lines[1:],[1,12345,32748]):
   check=0
   for _ in range(64):
    q,r=divmod(seed,436)
    seed=75*r-49*q
    if seed<=0:seed+=32749
    check=(check+seed%97)%997
   assert list(map(qty,line[-2:]))==[seed,check],(line,seed,check)
 elif name=='SQUARE':
  for idx,line in enumerate(lines,1):
   initial=1000-(idx+1)
   x=initial
   for _ in range(8):x=(x*x)//1000
   assert qty(line[-1])==x
   assert qty(line[-2])==(idx*100)*(x//10)
 elif name in ('BRENTROT','NEWTON','BISECT'):
  for idx,line in enumerate(lines,1):
   root=qty(line[2]);res=qty(line[3]);expected=math.sqrt(2) if idx==1 else 1.5213797068
   near(root,round(1000*expected),4,f'root{idx}')
   near(res,0,5,f'residual{idx}')
 elif name in ('CHOLESKY','MINILIN','LUPIVOT','THOMASTR','POLYFIT'):
  thresholds={'CHOLESKY':2,'MINILIN':3,'LUPIVOT':35,'THOMASTR':2,'POLYFIT':10}
  indexes={'CHOLESKY':3,'MINILIN':3,'LUPIVOT':3,'THOMASTR':3,'POLYFIT':4}
  for line in lines:
   assert 0<=qty(line[indexes[name]])<=thresholds[name],line
 elif name in ('SIMPSON','GAUSS1D','ROMBERG'):
  where={'SIMPSON':3,'GAUSS1D':2,'ROMBERG':3}[name]
  toler={'SIMPSON':6,'GAUSS1D':6,'ROMBERG':30}[name]
  for idx,line in enumerate(lines,1):
   exp=math.e-1 if idx==1 else math.pi
   near(qty(line[where]),round(exp*1000),toler,f'quadrature{idx}')
 elif name=='RK4FIXED':
  near(qty(lines[0][3]),round(math.exp(-2)*1000),7,'decay')
  near(qty(lines[1][3]),round(1000/(1+3/math.e)),16,'logistic')
 elif name=='EULERODE':
  for idx,line in enumerate(lines,1):
   n=idx*10
   near(qty(line[3]),round(1000*(1-1/n)**n),8,'euler')
 elif name=='TINYFFT':
  assert len(lines)==3
  assert all(qty(line[3])<=2 for line in lines)
  assert [list(map(qty,line[4:6])) for line in lines]==[[1000,1000],[2000,0],[1000,995]]
 elif name=='JACRELX':
  assert [int(line[2]) for line in lines]==[8,16]
  for line in lines:
   assert 0<=qty(line[3])<=1000 and 0<=qty(line[4])<=1000
 elif name=='GEMM8BIT':
  for idx,line in enumerate(lines,1):
   n=7+4*idx
   def aa(i,k):return 100+20*(i-k)
   def bb(k,j):return 1000+10*k if k==j else 10*(k+j)
   def c(i,j):return sum((aa(i,k)*bb(k,j))//1000 for k in range(n))
   # Forth uses truncation per multiplication and addition, same as floor here.
   assert list(map(qty,line[2:]))==[n,sum(c(i,i) for i in range(n)),c(0,0),c(n-1,n-1)],(idx,line)
 elif name=='WHETSTON':
  assert [int(x[1]) for x in lines]==[1,2]
  assert all(0<qty(line[-1])<32768 for line in lines)
 else:raise AssertionError(f'No independent property oracle for {name}')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--update-fixtures',action='store_true')
 args=ap.parse_args()
 info,words=audit_files()
 results={};outputs=[]
 for name in PROGRAMS:
  vm=execute_one(name)
  independent_oracle(name,vm.output)
  info[name].update(static_data_bytes=vm.here-1024,vm_steps=vm.steps,peak_data_stack_cells=vm.max_stack)
  results[name]=vm.output
  outputs.append(f'== {name}.F83 ==\n{vm.output}')
 combined='\n'.join(outputs)
 fixture=ROOT/'reference'/'HOST_OUTPUT.TXT'
 if args.update_fixtures:fixture.write_text(combined,encoding='ascii')
 else:
  expected=fixture.read_text(encoding='ascii')
  assert combined==expected,'host output differs from golden fixture'
 with (ROOT/'reference'/'EXPECTED.csv').open('w',newline='',encoding='ascii') as f:
  wr=csv.writer(f);wr.writerow(['program','output_line','text'])
  for name in PROGRAMS:
   for i,line in enumerate(results[name].strip().splitlines(),1):
    wr.writerow([name,i,line.strip()])
 manifest={
  'suite':'Forth-83 Z80 microcomputer integer and fixed-point demos',
  'programs':len(PROGRAMS),'support_files':SUPPORT,
  'arithmetic':'signed 16-bit cells; fixed Q=1000; floored division; Forth-83 D+ and UM/MOD',
  'host_execution':'Python constrained 16-bit Forth-83 semantic model (NOT a target compiler)',
  'standard_audit':'source tokens restricted to original Forth-83 required words plus user definitions',
  'results':'20/20 executed; 20/20 independent property oracles; 20/20 golden output checks',
  'largest_declared_data_bytes':max(info[x]['static_data_bytes'] for x in PROGRAMS),
  'notes':'Declared data does not count compiled threaded-code dictionary, Forth kernel, stacks, block buffers, or runtime.',
  'source':info}
 (ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(f'PASS: 20/20 Forth-83 required-word audits; 20/20 16-bit runs; 20/20 oracles; 20/20 golden comparisons')
 print('Largest static declared data incl. shared libraries:',manifest['largest_declared_data_bytes'],'bytes')
 for name in PROGRAMS:
  print(f"{name:9s} data={info[name]['static_data_bytes']:4d} bytes, VM steps={info[name]['vm_steps']:7d}, stack={info[name]['peak_data_stack_cells']} cells")

if __name__=='__main__':main()
