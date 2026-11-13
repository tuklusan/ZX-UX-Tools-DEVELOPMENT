 100 CLS 
 110 LET q=1+INT (4*RND)
 120 LET m=2+INT (20*RND)
 130 GO SUB q*1000
 200 INPUT r: PRINT r
 210 IF ABS (r-a)>.5 THEN GO TO 240
 220 PRINT "YES, the answer is ";a
 230 GO TO 250
 240 PRINT "SORRY, the answer was ";a
 250 INPUT "Press <ENTER> when ready";y$
 260 RUN 
1000 PRINT "What is the circumference of a  circle with radius ";m
1010 LET a=2*PI*m
1020 RETURN 
2000 PRINT "What is the area of a circle    with radius ";m
2010 LET a=PI*m*m
2020 RETURN 
3000 PRINT "What is the surface area of a   sphere with radius ";m
3010 LET a=(4/3)*PI*m*m
3020 RETURN 
4000 PRINT "What is the volume of a sphere  with radius ";m
4010 LET a=PI*m*m*m/3
4020 RETURN 
