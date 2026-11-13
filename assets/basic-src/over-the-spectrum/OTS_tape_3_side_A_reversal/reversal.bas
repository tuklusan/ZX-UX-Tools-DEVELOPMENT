 100 LET print=600
 110 LET reverse=400
 120 LET input=300
 130 LET size=9
 140 DIM a(size)
 150 FOR c=1 TO size
 160  LET a(c)=c
 170 NEXT c
 180 FOR c=size TO 2 STEP -1
 190  LET swap=1+INT (size*RND)
 200  LET temp=a(c)
 210  LET a(c)=a(swap)
 220  LET a(swap)=temp
 230 NEXT c
 240 LET count=0
 250 GO SUB print
 300 INPUT "How many numbers do you wish to reverse? ";howmany
 310 IF howmany=0 THEN STOP 
 320 IF howmany<=size THEN GO TO reverse
 330 PRINT size;" is maximum that can be swapped"
 340 GO TO input
 400 PRINT "Reversing ";howmany;" numbers"
 410 LET count=count+1
 420 FOR d=1 TO INT (howmany/2)
 430 LET temporary=a(d)
 440 LET mirror=howmany-d+1
 450 LET a(d)=a(mirror)
 460 LET a(mirror)=temporary
 470 NEXT d
 480 GO SUB print
 490 FOR d=1 TO size
 500 IF a(d)<>d THEN GO TO input
 510 NEXT d
 520 PRINT "You did it in ";count;" moves."
 530 STOP 
 600 POKE 23692,255
 610 FOR d=1 TO size
 620 PRINT a(d);" ";
 630 NEXT d
 640 PRINT 
 650 RETURN 
