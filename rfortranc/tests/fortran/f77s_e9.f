      PROGRAM E9TST
      REAL A,B
      A=0.125
      WRITE(6,10) A
   10 FORMAT(E17.9)
      READ(5,20) B
   20 FORMAT(E17.9)
      WRITE(6,30) B
   30 FORMAT(E18.9E3)
      END
