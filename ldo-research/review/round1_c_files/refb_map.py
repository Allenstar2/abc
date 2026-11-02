"""Quasi-static hole map with REF-B numbers (slice 12.2 mA, 8 slices)."""
import numpy as np
Is = 12.2
for name, lo, hi in (("narrow 8-14 mA", 8, 14), ("wide 3-18 mA", 3, 18)):
    holes = [(hi + Is*k, lo + Is*(k+1)) for k in range(8) if hi + Is*k < lo + Is*(k+1)]
    holes = [(a, b) for a, b in holes if a < 8*Is + hi]
    tot = sum(min(b, 100) - a for a, b in holes if a < 100)
    print(f"{name}: r = {(hi-lo)/Is:.3f}; LC load intervals (mA): " + ", ".join(f"({a:.1f},{b:.1f})" for a, b in holes if a < 100),
          f"; fraction of 0-100 mA = {tot/100:.2f}")
    for IL in (20, 45, 70, 95):
        k = [k for k in range(9) if lo <= IL - Is*k <= hi]
        print(f"   I_L={IL} mA -> codes inside window: {k if k else 'NONE -> LC'}")
