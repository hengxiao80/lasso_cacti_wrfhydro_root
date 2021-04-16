@vectorize([float64(float64, float64)])
def td_to_sh(p, tdk):
"""
ufunc to calculate specific humidity (kg/kg) from pressure (p in Pa) and dewpoint
temperature (td in K)

Following the algorithm in NCL

---From mixhum_ptd.f ---
C NCLFORTSTART
      SUBROUTINE DWMRQ (P,TD,PMSG,TDMSG,NMAX,WMR,WMRMSG,ISWIT)
      IMPLICIT NONE
      INTEGER  NMAX, ISWIT
      DOUBLE PRECISION P(NMAX), TD(NMAX),PMSG,TDMSG
      DOUBLE PRECISION WMR(NMAX),WMRMSG
C NCLEND
      DOUBLE PRECISION DWMRSKEWT
      EXTERNAL DWMRSKEWT

C ncl:   q = mixhum_ptd (p,td,option)   [ q=g/kg ]
c                        p  - PA
c                        td - K
C local
      INTEGER  N
      DOUBLE PRECISION T0, PA2MB
      DATA     T0    /273.15d0/
      DATA     PA2MB /0.01d0  /

C mixing ratio (kg/kg)
c the function wants hPA (mb) and degrees centigrade

      DO N=1,NMAX
         IF (TD(N).EQ.TDMSG.or.P(N).EQ.PMSG) then
             WMR(N) = WMRMSG
         ELSE
             WMR(N) = DWMRSKEWT(P(N)*PA2MB,(TD(N)-T0))*0.001d0
         END IF
      END DO

c if ISWIT=2 calculate specific humidity (kg/kg)

      IF (ABS(ISWIT).EQ.2) THEN
          DO N=1,NMAX
             IF (WMR(N).NE.WMRMSG) THEN
                 WMR(N) = (WMR(N)/(WMR(N)+1.d0))
             END IF
         END DO
      END IF

c if ISWIT < 0 then return g/kg

      IF (ISWIT.LT.0) THEN
          DO N=1,NMAX
             IF (WMR(N).NE.WMRMSG) THEN
                 WMR(N) = WMR(N)*1000.d0
             END IF
         END DO
      END IF

      RETURN
      END

--- From skewT.f ---
c -----------------------------------------
      DOUBLE PRECISION FUNCTION DWMRSKEWT(P,T)
      DOUBLE PRECISION P
      DOUBLE PRECISION T
      DOUBLE PRECISION EPS
      DOUBLE PRECISION X
      DOUBLE PRECISION WFW
      DOUBLE PRECISION FWESW
      DOUBLE PRECISION DESWSKEWT
      DOUBLE PRECISION R

c   this function approximates the mixing ratio wmr (grams of water
c   vapor per kilogram of dry air) given the pressure p (mb) and the
c   temperature t (celsius). the formula used is given on p. 302 of the
c   smithsonian meteorological tables by roland list (6th edition).

c   eps = ratio of the mean molecular weight of water (18.016 g/mole)
c         to that of dry air (28.966 g/mole)

      DATA EPS/0.62197D0/

c   the next two lines contain a formula by herman wobus for the
c   correction factor wfw for the departure of the mixture of air
c   and water vapor from the ideal gas law. the formula fits values
c   in table 89, p. 340 of the smithsonian meteorological tables,
c   but only for temperatures and pressures normally encountered in
c   in the atmosphere.

      X = 0.02D0* (T-12.5D0+7500.D0/P)
      WFW = 1.D0 + 4.5D-06*P + 1.4D-03*X*X
      FWESW = WFW*DESWSKEWT(T)
      R = EPS*FWESW/ (P-FWESW)

c   convert r from a dimensionless ratio to grams/kilogram.

      DWMRSKEWT = 1000.D0*R
      RETURN
      END

c -----------------------------------------
      DOUBLE PRECISION FUNCTION DESWSKEWT(T)
      DOUBLE PRECISION T
      DOUBLE PRECISION ES0
      DOUBLE PRECISION POL

c   this function returns the saturation vapor pressure esw (millibars)
c   over liquid water given the temperature t (celsius). the polynomial
c   approximation below is due to herman wobus, a mathematician who
c   worked at the navy weather research facility, norfolk, virginia,
c   but who is now retired. the coefficients of the polynomial were
c   chosen to fit the values in table 94 on pp. 351-353 of the smith-
c   sonian meteorological tables by roland list (6th edition). the
c   approximation is valid for -50 < t < 100c.
c
c   es0 = saturation vapor ressure over liquid water at 0c

      DATA ES0/6.1078D0/

      POL = 0.99999683D0 + T* (-0.90826951D-02+
     +      T* (0.78736169D-04+T* (-0.61117958D-06+T* (0.43884187D-08+
     +      T* (-0.29883885D-10+T* (0.21874425D-12+T* (-0.17892321D-14+
     +      T* (0.11112018D-16+T* (-0.30994571D-19)))))))))
      DESWSKEWT = ES0/POL**8
      RETURN
      END
"""
    td = tdk - 273.15
    es0 = 6.1078
    eps = 0.62197
    pa = [0.99999683, -0.90826951e-02, 0.78736169e-04, -0.61117958e-06,
          0.43884187e-08, -0.29883885e-10, 0.21874425e-12, -0.17892321e-14,
          0.11112018e-16, -0.30994571e-19]
    pol = pa[0] + td*(pa[1] +
                  td*(pa[2] +
                  td*(pa[3] +
                  td*(pa[4] +
                  td*(pa[5] +
                  td*(pa[6] +
                  td*(pa[7] +
                  td*(pa[8] + td*pa[9]))))))))
    # saturation vapor pressure
    esw = es0/(pol**8)
    # correction?
    x = 0.02 * (td - 12.5 + 7.5e5/p)
    eswc = (1.0 + 4.5e-08*p + 1.4e-03*x*x)*esw
    # water mixing ratio in kg/kg
    r = eps*eswc/((p*0.01) - ewsc)
    # specific humidity
    sh = r/(1.0 + r)
    return sh