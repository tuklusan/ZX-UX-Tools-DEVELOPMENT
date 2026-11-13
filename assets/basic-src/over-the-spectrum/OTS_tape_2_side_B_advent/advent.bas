   5 LET tr=1999: LET fa=1998: LET ls=9000: LET os=8000: LET oz=8500: LET vs=7000: LET cs=7100: LET sc=0
   6 LET vr=1480: LET z=0: LET ct=1997: LET dr=1601: LET cx=6: LET st=100
  10 BORDER 5: PAPER 7: INK 0: CLS 
  30 LET l=1
  40 GO SUB 900
  50 POKE 23692,255: RESTORE l+ls: READ m$: PRINT "You are ";m$: LET q$="You see": GO SUB 2000
  60 BEEP .2,12: PRINT 
  70 GO SUB 1000
  80 PRINT v$;" ";
  90 GO SUB vr+vn*20
 100 IF f=0 THEN GO TO 60
 110 PRINT : GO TO 50
 900 RESTORE os: READ oc: DIM o(oc)
 910 FOR i=1 TO oc: READ o(i): NEXT i
 920 RESTORE vs: READ vc
 930 LET be=0: LET lu=0: LET gu=0: LET e$="in an endless desert": LET p$="in a passage"
 940 RETURN 
1000 INPUT "Tell me what to do ";s$: IF LEN s$=0 THEN GO TO 1000
1010 LET a$="": LET n$=""
1020 LET x=0: FOR i=1 TO LEN s$
1030 LET i$=s$(i TO i)
1040 IF i$>="A" AND i$<="Z" THEN LET i$=CHR$ (32+CODE i$)
1050 IF i$=" " AND x=1 THEN LET i=LEN s$: GO TO 1080
1051 IF i$=" " THEN LET x=1: GO TO 1080
1060 IF x=0 THEN LET a$=a$+i$
1070 IF x=1 THEN LET n$=n$+i$
1080 NEXT i: LET w$=a$: LET c=vc: LET d=vs+1: GO SUB 1200
1090 IF vn=0 THEN PRINT "{14}{01}I don't understand{14}{00} ";a$: GO TO 1000
1100 LET v$=y$: RETURN 
1200 LET vn=0
1210 RESTORE d
1220 FOR i=1 TO c: READ m$: LET x=LEN m$: IF x>LEN w$ THEN LET x=LEN w$
1240 IF w$( TO x)=m$( TO x) THEN LET vn=i: LET y$=m$: LET i=c
1260 NEXT i: RETURN 
1300 IF n$="" THEN GO TO 1311
1301 LET w$=n$: LET c=oc: LET d=os+1: GO SUB 1200: IF vn=0 THEN GO TO 1311
1310 PRINT y$: GO TO tr
1311 PRINT "{14}{01}I don't understand{14}{00} ";n$: GO TO fa
1500 LET d=1: GO TO dr
1520 LET d=2: GO TO dr
1540 LET d=3: GO TO dr
1560 LET d=4: GO TO dr
1580 LET d=5: GO TO dr
1600 LET d=6
1601 PRINT : RESTORE l+ls: READ m$: FOR i=1 TO d: READ nl: NEXT i
1602 IF nl=0 THEN PRINT "You can't go that way": GO TO fa
1603 RESTORE nl+ls: READ m$,s,s,s,s,s,s
1604 READ s
1605 GO SUB cs+s: IF f=0 THEN GO TO 1611
1610 IF o(1)=0 THEN LET l=nl: GO TO tr
1611 PRINT "Something stops you": GO TO fa
1620 GO SUB 1300: IF f=0 THEN RETURN 
1621 IF o(vn)<>l THEN PRINT "It's not here": GO TO fa
1622 RESTORE oz+vn: READ s: IF s<0 THEN GO TO ct
1624 READ s
1625 READ s
1626 GO SUB cs+s: IF f=0 THEN GO TO ct
1630 IF cx<>0 THEN LET cx=cx-1: LET o(vn)=0: RETURN 
1631 PRINT "You are carrying too much": GO TO fa
1640 GO SUB 1300: IF f=0 THEN RETURN 
1641 IF o(vn)<>0 THEN PRINT "You don't have it": GO TO fa
1642 RESTORE oz+vn: READ s
1643 LET o(vn)=l: IF l=1 AND s<>0 THEN LET sc=sc+s: LET o(vn)=-1: PRINT "The ";y$;" vanishes"
1644 LET cx=cx+1: IF sc=220 THEN GO TO 9980
1645 RETURN 
1660 GO SUB 1300: IF f=0 THEN RETURN 
1661 LET t$=y$: LET mn=vn: RESTORE oz+vn: READ s,ms: IF s>=0 THEN GO TO ct
1662 LET s=0: BEEP .1,20: INPUT "kill with what ?";w$: IF w$="" THEN GO TO 1670
1663 LET c=oc: LET d=os+1: GO SUB 1200: IF vn=0 THEN GO TO 1662
1664 IF o(vn)<>0 THEN GO TO 1662
1665 RESTORE oz+vn: READ s,s: IF s=0 THEN GO TO 1662
1666 PRINT " with ";y$;
1670 PRINT : LET s=s+st: IF ms>s+RND*20 THEN GO TO 1679
1671 IF s>ms+RND*15 THEN GO TO 1678
1672 PRINT "The ";t$;" fights back. You feel weaker"
1673 LET st=st-RND*5: GO TO tr
1678 PRINT "You have killed the ";t$: PRINT "The body vanishes in a cloud of smoke": LET o(mn)=-1: GO TO tr
1679 PRINT "The ";t$;" has killed you": GO TO 9990
1680 LET l1=l: LET l=0: LET q$="You are carrying": GO SUB 2000: LET l=l1: GO TO tr
1700 PRINT sc: GO TO tr
1720 GO SUB 1300: IF f=0 THEN RETURN 
1721 IF vn<>20 OR o(2)<>0 THEN GO TO ct
1722 LET o(14)=o(vn): LET o(vn)=-1: PRINT "An ivory key falls from the     ceiling": RETURN 
1740 IF l<>11 AND l<>29 THEN GO TO ct
1741 IF l=11 AND o(3)<>0 THEN PRINT "You sink to the bottom of the   lake and drown": GO TO 9990
1742 IF l=11 THEN LET l=29: GO TO tr
1743 LET l=11: GO TO tr
1760 GO SUB 1300: IF f=0 THEN RETURN 
1761 IF l=1 AND o(4)=0 THEN LET o(22)=-1: LET o(23)=l: LET lu=1: RETURN 
1762 IF l=13 AND o(14)=0 THEN LET o(24)=-1: LET o(25)=l: LET gu=1: RETURN 
1763 GO TO ct
1780 IF o(16)<>0 OR l<3 OR l>10 THEN GO TO ct
1781 PRINT "You find ";
1782 IF l=6 AND o(4)=-1 THEN LET o(4)=l: PRINT "something": GO TO tr
1783 PRINT "nothing": GO TO tr
1800 GO SUB 1300: IF f=0 THEN RETURN 
1801 RESTORE oz+vn: READ s,s1,s1
1802 IF s<0 THEN GO TO ct
1803 GO SUB cs+s1: IF f=0 THEN GO TO ct
1804 PRINT "That hits the spot": LET o(vn)=-1: RETURN 
1820 GO SUB 1300: IF f=0 THEN RETURN 
1821 IF l<>24 OR vn<>7 THEN GO TO 1830
1822 PRINT "A bridge appears across the     chasm": LET o(15)=l: LET be=1: GO TO tr
1830 PRINT "Nothing happens": GO TO fa
1840 IF l=24 OR l=26 THEN PRINT "The fall has broken your neck": GO TO 9990
1841 GO TO 1830
1860 GO SUB 1300: IF f=0 THEN RETURN 
1861 IF vn<>18 THEN GO TO ct
1862 PRINT "That was delicious": LET o(19)=o(vn): LET o(vn)=-1: RETURN 
1997 PRINT "You can't"
1998 LET f=0: RETURN 
1999 LET f=1: RETURN 
2000 LET x=0: PRINT q$
2010 RESTORE os+1: FOR i=1 TO oc: READ m$
2020 IF l<>o(i) THEN GO TO 2030
2021 LET x=1: PRINT "  a";
2022 LET z$=m$(1 TO 1): IF z$="a" OR z$="e" OR z$="i" OR z$="o" OR z$="u" THEN PRINT "n";
2024 PRINT " ";m$
2030 NEXT i
2040 IF x=0 THEN PRINT "  nothing"
2050 RETURN 
7000 DATA 19
7001 DATA "north","south","east","west","up","down"
7002 DATA "take","drop","kill","inventory","score"
7003 DATA "cut","swim","unlock","dig"
7004 DATA "eat","wave","jump","drink"
7100 GO TO tr
7101 GO TO fa+lu
7102 GO TO fa+gu
7103 GO TO fa+be
7104 GO TO fa+(o(3)=0)
7105 GO TO fa+(o(11)=-1)
7106 GO TO fa+(o(12)=-1)
7107 GO TO fa+(o(10)=-1)
7150 IF o(18)<>0 THEN GO TO tr
7151 LET o(18)=-1: LET o(12)=-1: PRINT "As you enter a pirate steals    your rum and runs of laughing": GO TO tr
7160 PRINT "The devil kills you": GO TO 9990
8000 DATA 25,1,12,27,-1,14,17,21,25,29,12,14,17,20,-1,-1,11,2,2,-1,19,11,1,-1,13,-1
8001 DATA "brass lamp"
8002 DATA "sword"
8003 DATA "snorkel"
8004 DATA "large key"
8005 DATA "persian rug"
8006 DATA "gold coin"
8007 DATA "silver wand"
8008 DATA "ruby"
8009 DATA "diamond"
8010 DATA "mean troll"
8011 DATA "green dragon"
8012 DATA "pirate"
8013 DATA "devil"
8014 DATA "ivory key"
8015 DATA "crystal bridge"
8016 DATA "shovel"
8017 DATA "kitchen table"
8018 DATA "bottle of rum"
8019 DATA "empty bottle"
8020 DATA "rope tied between the floor and ceiling"
8021 DATA "small lake"
8022 DATA "locked door"
8023 DATA "door"
8024 DATA "padlocked gate"
8025 DATA "gate"
8501 DATA z,z,z
8502 DATA z,20,7
8503 DATA z,z,z
8504 DATA z,z,z
8505 DATA 10,z,5
8506 DATA 50,z,6
8507 DATA 20,z,z
8508 DATA 30,z,z
8509 DATA 100,z,z
8510 DATA -1,87,z
8511 DATA -1,110,z
8512 DATA -1,200,z
8513 DATA -1,200,z
8514 DATA 10,z,z
8515 DATA z,z,z
8516 DATA z,z,z
8517 DATA z,z,fa-cs
8518 DATA z,z,z
8519 DATA z,z,z
8520 DATA z,z,fa-cs
8521 DATA z,z,fa-cs
8522 DATA z,z,fa-cs
8523 DATA z,z,fa-cs
8524 DATA z,z,fa-cs
8525 DATA z,z,fa-cs
9001 DATA "in the living room of a large house. A sign says Return all treasures here.",2,z,z,z,z,12,z
9002 DATA "in the kitchen",z,1,3,z,z,z,z,z
9003 DATA e$,z,4,5,2,z,z,z
9004 DATA e$,3,7,6,z,z,z,z
9005 DATA e$,z,6,7,3,z,z,z
9006 DATA e$,5,8,z,4,z,z,z
9007 DATA e$,z,z,z,4,z,z,z
9008 DATA e$,6,9,z,z,z,z,z
9009 DATA e$,8,z,10,z,z,z,z
9010 DATA e$,11,z,z,9,z,z,z
9011 DATA "at an oasis",z,10,z,z,z,z,z
9012 DATA "in a cellar",z,16,13,z,1,z,1
9013 DATA "at the {10}{02}GATES OF HELL{10}{00}",z,z,z,12,z,20,z
9014 DATA "in a {14}{01}blackened cavern{14}{00}",z,15,z,z,z,z,z
9015 DATA p$,14,18,z,16,z,z,z
9016 DATA p$,12,z,15,z,z,17,z
9017 DATA "in the pirates lair",z,z,z,z,16,z,50
9018 DATA p$,15,19,z,z,z,z,z
9019 DATA p$,18,z,z,z,z,z,z
9020 DATA "in HELL... A devil says 'Find the right direction and  live - {10}{02}else die{10}{00}'",30,30,30,21,30,30,2
9021 DATA p$,z,24,22,20,z,z,z
9022 DATA "in a dead end",z,z,z,21,z,z,z
9023 DATA "{11}{00}{10}{02}DEAD IN HELL{11}{07}{10}{00}",z,z,z,z,z,z,z
9024 DATA "at the brink of a deep  chasm",21,25,z,z,z,z,z
9025 DATA "in a beautiful jewelled hall",24,z,27,z,z,z,3
9026 DATA "at the brink of a deep  pit. There are traces of {10}{02}fire{10}{00}   and {11}{06}brimstone{11}{07} here.",z,27,z,z,z,23,z
9027 DATA p$,26,z,z,25,z,28,z
9028 DATA p$,z,z,z,z,27,18,z
9029 DATA "{10}{01}swimming in a small lake{10}{00}",z,z,z,z,z,z,4
9030 DATA "",z,z,z,z,z,z,60
9980 PRINT : PRINT : PRINT : PRINT 
9981 PRINT "CONGRATULATIONS   This adventureis over and you have returned   safely with all the treasures."
9990 PRINT : PRINT "SCORE ";sc: PRINT "Do you wish to play again ?"
9991 LET m$=INKEY$: IF m$="" THEN GO TO 9991
9992 IF m$( TO 1)="y" THEN GO TO 5
