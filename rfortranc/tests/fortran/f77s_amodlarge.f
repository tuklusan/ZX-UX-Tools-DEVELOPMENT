      PROGRAM MODBIG
      REAL A,B,C
      A=AMOD(100000.0,3.0)
      B=AMOD(-100000.0,3.0)
      C=AMOD(100000.0,-3.0)
      WRITE (6,10) A,B,C
   10 FORMAT(3F8.2)
      END
