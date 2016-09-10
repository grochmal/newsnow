#!/usr/bin/env python3

# x is a number between 1 and 553 such that the sum of x's divisors (not
# including x) is greater than x but no subset of x's divisors add up to
# exactly x.

import itertools as i

pos = list(range(1,554))
#pos = list(range(1,20))
#pos.reverse()  # assumption: it is more likely to find it at the end
                # (turned out to be a bad assumption)
print(pos)

def is_divisor(x, n):
    if 0 == n%x: return True
    else:        return False

# https://docs.python.org/3/library/itertools.html#itertools-recipes
def powerset(iterable):
    s = list(iterable)
    return i.chain.from_iterable(i.combinations(s,r) for r in range(len(s)+1))

for n in pos:
    divisors = list(filter(lambda x: is_divisor(x, n), list(range(1, n//2+1))))
    print(n, divisors)
    the_sum = sum(divisors)
    print('sum:', the_sum)
    if the_sum <= n:
        continue
    subset_ok = True
    for subset in powerset(divisors):
      print('subset', subset)
      if sum(subset) == n:
          print('sum ==', n)
          subset_ok = False
          break
    if subset_ok:
        print('We found it:', n)
        break

