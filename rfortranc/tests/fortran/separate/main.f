C     F77S main unit, separately compiled with STEPER.
      PROGRAM SEPM
      INTEGER N
      N=40
      CALL STEPER(N)
      WRITE(6,10) N
   10 FORMAT(I4)
      END
