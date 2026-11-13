 100 LET a$="{8F} {8F} {8F} {8F}   {89} {89} {89} {89}"
 110 LET b$=a$
 120 LET count=0
 130 CLS 
 140 PRINT AT 5,3;b$;AT 6,3;"1 2 3 4 5 6 7 8 9"
 150 IF b$(1 TO 7)=a$(11 TO 17) AND b$(11 TO 17)=a$(1 TO 7) THEN GO TO 250
 160 INPUT "Please enter your move";k$
 170 IF LEN k$<>2 THEN GO TO 160
 180 LET from=2*(CODE k$(1)-48)-1
 190 LET to=2*(CODE k$(2)-48)-1
 200 IF b$(to)<>" " OR ABS (to-from)>4 THEN GO TO 160
 210 LET count=count+1
 220 LET b$(to)=b$(from)
 230 LET b$(from)=" "
 240 GO TO 140
 250 PRINT "You did it in ";count;" moves"
 260 INPUT "Another go?";k$
 270 IF CODE k$=65 THEN RUN 
