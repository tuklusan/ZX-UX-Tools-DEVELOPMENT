   1 PAPER 7: BORDER 7: CLS 
   2 LET p=248: LET t=31: LET a=128: LET g=13: LET h=160
   3 LET b=192: LET d=224: LET e=240: LET f=15
   4 LET x=0: LET y=1: LET z=3: LET c=7: LET i=160
   5 LET f$="": DIM A$(1,1)
   6 LET kx=5: LET ky=8: LET q=0
  10 FOR m=USR "a" TO USR "t"+7
  20 READ n: POKE m,n: NEXT m
  30 DATA x,x,x,x,x,x,y,z
  40 DATA x,x,x,x,x,x,a,b
  50 DATA c,c,z,y,z,c,x,x
  60 DATA d,d,b,a,b,d,x,x
  70 DATA y,c,c,y,g,f,f,c
  80 DATA a,d,d,a,176,e,e,d
  90 DATA z,z,z,y,c,f,31,x
 100 DATA b,b,b,a,d,e,p,x
 110 DATA 4,5,2,y,z,c,c,c
 120 DATA 32,h,64,a,b,d,d,d
 130 DATA z,y,y,y,z,c,f,x
 140 DATA b,a,a,a,b,d,e,x
 150 DATA y,z,c,c,14,g,c,z
 160 DATA a,b,h,112,e,d,d,b
 170 DATA x,x,x,x,x,5,5,c
 180 DATA x,x,x,x,x,h,h,d
 190 DATA x,x,x,y,z,c,c,z
 200 DATA x,x,a,b,d,e,p,152
 210 DATA y,y,y,z,c,c,f,x
 220 DATA a,a,a,b,d,d,e,x
 230 DIM t$(7,2): DIM b$(7,2)
 240 FOR x=1 TO 7: READ t$(x),b$(x): NEXT x
 250 DATA "{90}{91}","{92}{93}","{A0}{A1}","{A2}{A3}"
 260 DATA "{9C}{9D}","{9A}{9B}","{9E}{9F}","{92}{93}"
 270 DATA "{98}{99}","{9A}{9B}","{94}{95}","{96}{97}","  ","  "
 280 LET i=2: LET p=4: PRINT "  A B C D E F G H"
 290 PRINT : FOR x=0 TO 7: FOR y=0 TO 1: PRINT ;"  ";
 300 FOR z=0 TO 3: PRINT PAPER p;"  "; PAPER i;"  ";
 310 NEXT z: PRINT : NEXT y: LET t=i: LET i=p: LET p=t: NEXT x
 315 FOR y=1 TO 8: PRINT AT y+y,0;y: NEXT y
 320 DIM b(8,8): FOR y=1 TO 8: FOR x=1 TO 8
 330 LET z=(y=8)*-b(x,1)+(y=2)*-1+(y=7)
 340 IF y=1 THEN READ z
 350 LET b(x,y)=z: NEXT x: NEXT y
 360 DATA -4,-2,-3,-5,-6,-3,-2,-4
 370 GO SUB 2000
 380 DIM d(6,8,2): DIM p(6)
 390 FOR x=1 TO 6: LET p(x)=2: FOR y=1 TO 8
 400 LET d(x,y,2)=((y<3) OR (y=8))+((y>3) AND (y<7))*-1
 410 LET d(x,y,1)=((y>1) AND (y<5))+(y>5)*-1
 420 NEXT y: IF x<>2 THEN GO TO 460
 430 FOR y=1 TO 4: READ d(x,y,1),d(x,y,2): LET d(x,y+4,1)=-d(x,y,1): LET d(x,y+4,2)=-d(x,y,2)
 440 NEXT y
 450 DATA -2,1,-1,2,1,2,2,1
 460 IF x=1 THEN LET p(x)=8
 470 IF x>4 THEN LET p(x)=1
 480 NEXT x
 490 DIM c$(5): FOR x=1 TO 5: READ c$(x): NEXT x
 500 DATA "p","n","b","r","q"
 600 GO SUB 3000
 610 PRINT AT 8,22; FLASH 1;"THINKING";
 620 GO SUB 4000
 630 GO TO 600
 800 LET A$(1)=INKEY$: IF A$(1)="p" THEN GO TO 900
 805 IF (A$(1)="") OR (A$(1)<"a") OR (A$(1)>"h") THEN GO TO 800
 810 PRINT A$(1);" ";
 820 LET X1=CODE A$(1)-96
 830 LET A$(1)=INKEY$: IF (A$(1)="") OR (A$(1)<"1") OR (A$(1)>"8") THEN GO TO 830
 840 PRINT A$(1);
 850 LET Y1=CODE A$(1)-48
 860 RETURN 
 900 LET X1=999: LET Y1=0: RETURN 
1000 LET z1=INT ((ATTR (y+y,x+x))/8): IF z1>=8 THEN LET z1=z1-8
1010 PRINT BRIGHT 1; PAPER z1; INK i;AT y+y,x+x;t$(c);AT y+y+1,x+x;b$(c);
1020 RETURN 
2000 FOR y=1 TO 8: FOR x=1 TO 8
2010 LET z=b(x,y): IF z=0 THEN GO TO 2040
2020 LET i=7: IF z>0 THEN LET i=0
2030 LET c=ABS z: GO SUB 1000
2040 NEXT x: NEXT y
2050 RETURN 
3000 IF f$="1" THEN PRINT AT 20,22;"CHECKMATE": STOP 
3010 PRINT AT 3,22;"Your move": PRINT AT 4,22;"FROM ";: GO SUB 800: IF X1=999 THEN STOP 
3020 LET X=X1: LET Y=Y1
3030 PRINT AT 5,24;"TO ";: GO SUB 800: LET XB=X1: LET YB=Y1
3040 IF b(XB,YB)>0 THEN LET p(b(XB,YB))=p(b(XB,YB))-1
3050 LET b(XB,YB)=b(X,Y)
3060 LET b(X,Y)=0: LET i=7
3070 IF b(XB,YB)<-1 OR YB<8 THEN GO TO 3120
3080 PRINT AT 6,21;"Piece ";
3090 LET A$(1)=INKEY$:
3100 LET a=0: FOR z=1 TO 5: IF c$(z)=A$(1) THEN LET a=-z
3110 NEXT z: IF a=0 THEN GO TO 3090
3115 PRINT A$(1);: LET b(XB,YB)=a
3120 LET c=7: GO SUB 1000
3130 LET c=-b(XB,YB): LET x=XB: LET y=YB: GO SUB 1000
3140 PRINT AT 3,22;"         ";AT 4,22;"        ";AT 5,24;"      ";AT 6,21;"       ";
3150 RETURN 
4000 LET xb=0: LET yb=xb: LET db=xb: LET cl=1: LET bp=xb: LET x=9
4010 LET ax=kx: LET ay=ky: LET g$="": GO SUB 5010: LET g$=f$
4020 FOR y=1 TO 8: FOR x=1 TO 8: LET tb=0: LET cz=1: LET ty=0: LET tx=0: LET d=0
4030 IF b(x,y)<1 THEN GO TO 4370
4040 LET p=b(x,y): FOR i=1 TO 8: LET dy=d(p,i,2): LET dx=d(p,i,1): LET ax=kx: LET ay=ky: LET c1=1: LET po=0
4050 IF x+dx<1 OR x+dx>8 OR y+dy<1 OR y+dy>8 THEN GO TO 4300
4060 IF p>2 AND p<6 THEN GO TO 4210
4070 IF dy>-1 AND p=1 THEN GO TO 4300
4080 IF y>1 OR p>1 THEN GO TO 4130
4090 LET p(5)=p(5)+1
4100 LET b(x,y)=5
4120 GO TO 4300
4130 IF dx<>0 AND b(x+dx,y+dy)>-1 THEN GO TO 4300
4140 IF p=6 THEN LET kx=x: LET ky=y: LET ax=x+dx: LET ay=y+dy: GO SUB 5000: IF f$="1" THEN GO TO 4300
4150 IF dx=0 AND b(x,y+dy)<>0 THEN GO TO 4300
4160 LET po=8-p-b(x+dx,y+dy)*3
4170 IF y<>7 OR dx<>0 OR b(x,5)<>0 OR p>1 THEN GO TO 4300
4180 IF g$="1" THEN GO SUB 5000: IF f$="" THEN GO TO 4300
4190 IF g$="1" OR RND>.3 THEN LET c1=2
4200 GO TO 4300
4210 LET x1=x: LET y1=y
4220 IF p=3 AND INT (i/2)*2<i THEN GO TO 4300
4230 IF p=4 AND INT (i/2)*2=i THEN GO TO 4300
4240 IF x1+dx<1 OR x1+dx>8 OR y1+dy<1 OR y1+dy>8 THEN LET c1=c1-1: GO TO 4300
4250 IF b(x1+dx,y1+dy)>0 THEN LET c1=c1-1: GO TO 4300
4260 LET po=8-p+INT (RND*3)-b(x1+dx,y1+dy)*3
4270 IF g$="1" THEN GO SUB 5000: IF f$="" THEN LET po=po+50: GO TO 4340
4280 IF b(x1+dx,y1+dy)<>0 THEN GO TO 4300
4290 LET c1=c1+1: LET x1=x1+dx: LET y1=y1+dy: GO TO 4240
4300 IF po=0 THEN GO TO 4340
4310 IF g$="1" THEN GO SUB 5000: IF f$="" THEN LET po=po+50: GO TO 4340
4320 IF g$="" THEN GO SUB 5000: IF f$="1" THEN LET po=0: GO TO 4340
4330 IF po>=tb THEN LET ax=x+dx*c1: LET ay=y+dy*c1: GO SUB 5000: IF f$="1" THEN LET po=po-p*2
4340 IF po>tb THEN LET tb=po: LET tx=x: LET ty=y: LET d=i: LET cz=c1
4350 NEXT i
4360 IF tb>bp OR (tb=bp AND (RND>.9 OR (ty<yb AND RND>.5))) THEN LET bp=tb: LET xb=tx: LET yb=ty: LET cl=cz: LET db=d
4370 NEXT x: NEXT y: LET p=b(xb,yb): LET x1=xb+d(p,db,1)*cl: LET y1=yb+d(p,db,2)*cl: IF p=6 THEN LET kx=x1: LET ky=y1
4380 LET ax=kx: LET ay=ky: LET b(x1,y1)=b(xb,yb): LET b(xb,yb)=0: LET q=1: GO SUB 5010: LET q=0
4385 PRINT AT 8,22;"        ";AT 9,22;"My move";AT 10,22;"FROM ";CHR$ (xb+95);"-";CHR$ (yb+48);
4386 PRINT AT 11,24;"TO ";CHR$ (x1+95);"-";CHR$ (y1+48);
4390 LET i=0: LET c=7: LET x=xb: LET y=yb: GO SUB 1000
4400 LET c=b(x1,y1): LET x=x1: LET y=y1: GO SUB 1000
4410 RETURN 
5000 LET pc=b(x+dx*c1,y+dy*c1): LET b(x+dx*c1,y+dy*c1)=b(x,y): LET b(x,y)=0
5010 LET f$="": FOR r=1 TO 6: FOR j=1 TO 8: LET d1=d(r,j,1): LET d2=d(r,j,2): LET l=1
5020 IF ax+d1*l<1 OR ax+d1*l>8 OR ay+d2*l<1 OR ay+d2*l>8 THEN GO TO 5060
5030 IF r=1 AND d2<1 AND q=0 THEN GO TO 5060
5040 IF b(ax+d1*l,ay+d2*l)=-r THEN LET f$="1": GO TO 5070
5050 IF r>2 AND r<6 AND b(ax+d1*l,ay+d2*l)=0 THEN LET l=l+1: GO TO 5020
5060 NEXT j: NEXT r
5070 IF x>8 THEN GO TO 5090
5080 LET b(x,y)=b(x+dx*c1,y+dy*c1): LET b(x+dx*c1,y+dy*c1)=pc
5090 RETURN 
