 100 BORDER 7: PAPER 7: INK 0: OVER 0: CLS 
 110 RESTORE 600
 120 FOR i=USR "a" TO USR "d"-1
 130 READ x: POKE i,x: NEXT i
 140 LET n=15
 150 DIM p(n)
 160 PRINT "Do you want to choose your own  numbers (y or n)?"
 170 LET b$=INKEY$: IF b$="" THEN GO TO 170
 180 IF b$="n" OR b$="N" THEN GO TO 240
 190 PRINT "Enter 15 numbers to be sorted"
 200 FOR y=1 TO n
 210 INPUT p(y): PRINT p(y)
 220 NEXT y
 230 GO TO 270
 240 FOR x=1 TO n
 250 LET p(x)=15*RND+1
 260 NEXT x
 270 CLS 
 280 FOR x=1 TO n
 290 PRINT AT x,0;p(x)
 300 NEXT x
 310 LET m=18
 320 FOR j=1 TO n-1
 330 FOR i=j+1 TO n
 340 LET l=n+j-i+1
 350 IF p(j)<=p(l) THEN GO TO 500
 360 LET b$="         "( TO LEN STR$ p(j)): PRINT AT j,0; OVER 1; PAPER 5;b$
 370 IF l=m THEN GO TO 390
 380 FOR x=m TO l STEP SGN (l-m): PRINT INK 2;AT x,18;"{90}{91}{92}";AT x+SGN (m-l),18;"   ": NEXT x
 390 LET y=LEN STR$ p(l): FOR x=17 TO y STEP -1: PRINT INK 2;AT l,x;"{90}{91}{92} ": NEXT x
 400 FOR x=0 TO 10: PRINT AT l,x;" ";p(l); INK 2;"{90}{91}{92}": NEXT x
 410 FOR x=l TO j STEP -1: PRINT AT x,11;p(l); INK 2;"{90}{91}{92}";AT x+1,11;"             ": NEXT x
 420 PRINT OVER 1;AT j,0;p(j)
 430 FOR x=j TO l: PRINT OVER 1;AT x,0;p(j);AT x,0;p(j): NEXT x: PRINT AT l,0;p(j)
 440 FOR x=10 TO 0 STEP -1: PRINT AT j,x;p(l); INK 2;"{90}{91}{92}";" ": NEXT x
 450 FOR x=y TO 17: PRINT AT j,x; INK 2;" {90}{91}{92}": NEXT x
 460 LET m=j
 470 LET t=p(l)
 480 LET p(l)=p(j)
 490 LET p(j)=t
 500 NEXT i
 510 NEXT j
 520 FOR x=m TO 18: PRINT AT x,18; INK 2;"{90}{91}{92}";AT x-1,18;"   ": NEXT x
 530 PRINT AT 21,0;"Do you want to sort again? "
 540 LET b$=INKEY$: IF b$="" THEN GO TO 540
 550 IF b$="y" OR b$="Y" THEN RUN 100
 560 IF b$="y" OR b$="Y" THEN RUN 100
 600 DATA 0,0,2,6,15,30,63,254
 610 DATA 0,0,63,127,241,100,238,4
 620 DATA 63,255,241,228,158,223,14,4
