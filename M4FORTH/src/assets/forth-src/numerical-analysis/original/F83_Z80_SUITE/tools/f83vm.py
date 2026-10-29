"""Constrained 16-bit Forth-83 execution model for suite validation.
Not an independently certified Forth-83 implementation or Z80 compiler.
Implements only words used by this suite; no host floating point in execution.
"""
import re, sys
from pathlib import Path

class VMError(RuntimeError): pass

class VM:
 def __init__(self):
  self.words={};self.stack=[];self.rstack=[];self.loops=[];self.memory={};self.here=1024
  self.output='';self.current=None;self.ctrl=[];self.pending=None;self.steps=0
  self.max_steps=6000000;self.max_stack=0;self.peak_mem=0
 def norm(self,n):
  n=int(n)&65535
  return n if n<32768 else n-65536
 def pop(self):
  if not self.stack: raise VMError('data stack underflow')
  return self.stack.pop()
 def push(self,x):
  self.stack.append(self.norm(x));self.max_stack=max(len(self.stack),self.max_stack)
  if len(self.stack)>256: raise VMError('stack runaway')
 def get(self,a):
  if a%2 or a<1024 or a>=self.here: raise VMError(f'misaligned/out-of-bounds cell @{a}; here {self.here}')
  return self.memory.get(a,0)
 def put(self,a,x):
  if a%2 or a<1024 or a>=self.here: raise VMError(f'misaligned/out-of-bounds store !{a}; here {self.here}')
  self.memory[a]=self.norm(x)
 def bin(self,fn):
  b=self.pop();a=self.pop();self.push(fn(a,b))
 def raw(self,fn):
  fn(self)
 def tokenise(self,text):
  toks=[];i=0;L=len(text)
  while i<L:
   if text[i].isspace():i+=1;continue
   if text[i]=='(' and (i==0 or text[i-1].isspace()):
    j=text.find(')',i+1)
    if j<0:raise VMError('unclosed ( comment )')
    i=j+1;continue
   if text.startswith('\\',i) and (i==0 or text[i-1].isspace()):
    j=text.find('\n',i);i=L if j<0 else j+1;continue
   if text.startswith('."',i):
    i+=2
    if i<L and text[i]==' ':i+=1
    j=text.find('"',i)
    if j<0:raise VMError('unclosed ."')
    toks.append(('string',text[i:j]));i=j+1;continue
   j=i
   while j<L and not text[j].isspace():j+=1
   toks.append(('word',text[i:j].upper()));i=j
  return toks
 def call(self,name):
  if name in self.words:
   kind,obj=self.words[name]
   if kind=='var':self.push(obj)
   elif kind=='const':self.push(obj)
   elif kind=='code':self.execute(obj)
   else:raise VMError('bad word kind')
   return
  s=self.stack
  if name=='+':self.bin(lambda a,b:a+b)
  elif name=='-':self.bin(lambda a,b:a-b)
  elif name=='*':self.bin(lambda a,b:a*b)
  elif name=='/':self.bin(lambda a,b:a//b)
  elif name=='MOD':self.bin(lambda a,b:a%b)
  elif name=='/MOD':
   b=self.pop();a=self.pop();self.push(a%b);self.push(a//b)
  elif name=='*/':
   c=self.pop();b=self.pop();a=self.pop()
   if c==0:raise VMError('division zero */')
   val=(a*b)//c
   if val<-32768 or val>32767:raise VMError(f'*/ quotient overflow {val}')
   self.push(val)
  elif name=='*/MOD':
   c=self.pop();b=self.pop();a=self.pop()
   q=(a*b)//c;self.push((a*b)-q*c);self.push(q)
  elif name=='D+':
   bhi=self.pop()&65535;blo=self.pop()&65535
   ahi=self.pop()&65535;alo=self.pop()&65535
   total=(ahi*65536+alo+bhi*65536+blo)&0xffffffff
   self.push(total&65535);self.push(total>>16)
  elif name=='UM/MOD':
   den=self.pop()&65535;hi=self.pop()&65535;lo=self.pop()&65535
   if den==0:raise VMError('UM/MOD divide by zero')
   q,r=divmod(hi*65536+lo,den)
   if q>65535:raise VMError('UM/MOD quotient overflow')
   self.push(r);self.push(q)
  elif name=='DUP':self.push(s[-1])
  elif name=='DROP':self.pop()
  elif name=='SWAP':a=self.pop();b=self.pop();self.push(a);self.push(b)
  elif name=='OVER':self.push(s[-2])
  elif name=='ROT':c=self.pop();b=self.pop();a=self.pop();self.push(b);self.push(c);self.push(a)
  elif name=='?DUP':
   if s[-1]:self.push(s[-1])
  elif name=='1+':self.push(self.pop()+1)
  elif name=='1-':self.push(self.pop()-1)
  elif name=='2+':self.push(self.pop()+2)
  elif name=='2-':self.push(self.pop()-2)
  elif name=='2/':self.push(self.pop()//2)
  elif name=='NEGATE':self.push(-self.pop())
  elif name=='ABS':self.push(abs(self.pop()))
  elif name=='MIN':self.bin(min)
  elif name=='MAX':self.bin(max)
  elif name=='=':self.bin(lambda a,b: -1 if a==b else 0)
  elif name=='<':self.bin(lambda a,b: -1 if a<b else 0)
  elif name=='>':self.bin(lambda a,b: -1 if a>b else 0)
  elif name=='0=':self.push(-1 if self.pop()==0 else 0)
  elif name=='0<':self.push(-1 if self.pop()<0 else 0)
  elif name=='0>':self.push(-1 if self.pop()>0 else 0)
  elif name=='AND':self.bin(lambda a,b:a&b)
  elif name=='OR':self.bin(lambda a,b:a|b)
  elif name=='XOR':self.bin(lambda a,b:a^b)
  elif name=='NOT':self.push(~self.pop())
  elif name=='@':self.push(self.get(self.pop()))
  elif name=='!':a=self.pop();v=self.pop();self.put(a,v)
  elif name=='+!':a=self.pop();v=self.pop();self.put(a,self.get(a)+v)
  elif name=='>R':self.rstack.append(self.pop())
  elif name=='R>':self.push(self.rstack.pop())
  elif name=='R@':self.push(self.rstack[-1])
  elif name=='I':self.push(self.loops[-1]['i'])
  elif name=='J':self.push(self.loops[-2]['i'])
  elif name=='.':self.output+=f'{self.pop()} '
  elif name=='U.':self.output+=f'{self.pop()&65535} '
  elif name=='CR':self.output+='\n'
  elif name=='SPACE':self.output+=' '
  elif name=='DECIMAL':pass
  elif name==',':
   n=self.pop();self.here+=2;self.peak_mem=max(self.peak_mem,self.here);self.put(self.here-2,n)
  elif name=='ALLOT':
   n=self.pop();self.here+=n;self.peak_mem=max(self.peak_mem,self.here)
   if self.here%2:raise VMError('odd alignment by ALLOT')
  else:raise VMError(f'unknown word {name}')
 def execute(self,code):
  pc=0;depth0=len(self.loops);depthr=len(self.rstack)
  while pc<len(code):
   self.steps+=1
   if self.steps>self.max_steps:raise VMError('step ceiling')
   op,attr=code[pc];pc+=1
   if op=='lit':self.push(attr)
   elif op=='call':self.call(attr)
   elif op=='str':self.output+=attr
   elif op=='jz':
    if self.pop()==0:pc=attr
   elif op=='jmp':pc=attr
   elif op=='do':
    start=self.pop();limit=self.pop()
    if start==limit:raise VMError('zero-trip DO (unportable Forth-83)')
    self.loops.append({'i':start,'limit':limit,'begin':pc,'end':attr})
   elif op=='loop':
    l=self.loops[-1];n=self.norm(l['i']+1)
    if n==l['limit']:self.loops.pop()
    else:l['i']=n;pc=attr
   elif op=='exit':break
   else:raise VMError(f'bad op {op}')
  if len(self.loops)!=depth0 or len(self.rstack)!=depthr:
   raise VMError(f'loop/return stack unbalanced for {code[:4]}')
 def read(self,src):
  tk=self.tokenise(src);i=0
  while i<len(tk):
   kind,w=tk[i];i+=1
   if kind=='string':
    if self.current is None:raise VMError('compile-only ." outside definition')
    self.current.append(('str',w));continue
   if w==':':
    if self.current is not None:raise VMError('nested :')
    name=tk[i][1];i+=1;self.pending=name;self.current=[];self.ctrl=[];continue
   if w==';':
    if self.current is None or self.ctrl:raise VMError('bad ; or unresolved structures')
    self.words[self.pending]=('code',self.current)
    self.current=None;self.pending=None;continue
   if w in ('VARIABLE','CREATE','CONSTANT'):
    if self.current is not None:raise VMError('defining word in colon')
    name=tk[i][1];i+=1
    if name in self.words:raise VMError('redefinition '+name)
    if w=='CONSTANT':self.words[name]=('const',self.pop())
    elif w=='VARIABLE':
     self.words[name]=('var',self.here);self.here+=2;self.peak_mem=max(self.peak_mem,self.here)
    else:self.words[name]=('var',self.here)
    continue
   if self.current is None:
    if re.fullmatch('-?[0-9]+',w):self.push(int(w))
    else:self.call(w)
    continue
   c=self.current
   if w=='IF':self.ctrl.append(('if',len(c)));c.append(('jz',None))
   elif w=='ELSE':
    typ,pos=self.ctrl.pop()
    if typ!='if':raise VMError('bad ELSE')
    c.append(('jmp',None));c[pos]=('jz',len(c));self.ctrl.append(('else',len(c)-1))
   elif w=='THEN':
    typ,pos=self.ctrl.pop()
    if typ not in ('if','else'):raise VMError('bad THEN')
    c[pos]=(c[pos][0],len(c))
   elif w=='BEGIN':self.ctrl.append(('begin',len(c)))
   elif w=='WHILE':self.ctrl.append(('while',len(c)));c.append(('jz',None))
   elif w=='REPEAT':
    typ1,p1=self.ctrl.pop();typ2,p2=self.ctrl.pop()
    if (typ1,typ2)!=('while','begin'):raise VMError('bad REPEAT')
    c.append(('jmp',p2));c[p1]=('jz',len(c))
   elif w=='UNTIL':
    typ,pos=self.ctrl.pop()
    if typ!='begin':raise VMError('bad UNTIL')
    c.append(('jz',pos))
   elif w=='DO':self.ctrl.append(('do',len(c)));c.append(('do',None))
   elif w=='LOOP':
    typ,pos=self.ctrl.pop()
    if typ!='do':raise VMError('bad LOOP')
    c.append(('loop',pos+1));c[pos]=('do',len(c))
   elif w=='EXIT':c.append(('exit',None))
   elif re.fullmatch('-?[0-9]+',w):c.append(('lit',int(w)))
   else:c.append(('call',w))
 def load(self,path):
  try:self.read(Path(path).read_text(encoding='ascii'))
  except Exception as e:raise VMError(f'{path}: {e}') from e

def suite_run(directory):
 p=Path(directory)
 for name in ['WHETSTON','MACHAR','LCGRAND','SQUARE','MINILIN','GEMM8BIT','LUPIVOT','THOMASTR','CHOLESKY','BRENTROT','NEWTON','BISECT','ROMBERG','SIMPSON','GAUSS1D','RK4FIXED','EULERODE','JACRELX','TINYFFT','POLYFIT']:
  m=VM();m.load(p/'COMMON.F83')
  if name in ('MINILIN','LUPIVOT','POLYFIT'):m.load(p/'LINCORE.F83')
  m.load(p/(name+'.F83'))
  if m.stack:raise VMError(f'{name}: data stack not balanced {m.stack}')
  print(name, 'steps',m.steps,'data_bytes',m.here-1024,'max_stack',m.max_stack,'OUTPUT:',repr(m.output))
if __name__=='__main__':suite_run(sys.argv[1])
