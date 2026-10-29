      PROGRAM F9TEST
      REAL A,B,C
      A=0.125
      C=-0.5
      WRITE(6,10) A,C
   10 FORMAT(2F16.9)
      READ(5,20) B
   20 FORMAT(F16.9)
      WRITE(6,30) B
   30 FORMAT(F16.9)
      END
