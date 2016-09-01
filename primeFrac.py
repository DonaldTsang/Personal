def testDiv(primfac, n, p):
	ctr = 0
	while n % p == 0:
		ctr += 1; n //= p
	if ctr != 0: primfac += [(p, ctr)]
	return n

def primes(n):
	primfac = []
	n = testDiv(primfac, n, 2)
	n = testDiv(primfac, n, 3)
	n = testDiv(primfac, n, 5)
	counter, d = 0, 7
	while d ** 2 <= n:
		n = testDiv(primfac, n, d)
		d += 4
		if d ** 2 > n: break
		n = testDiv(primfac, n, d)
		d += 2
		if d ** 2 > n: break
		n = testDiv(primfac, n, d)
		d += 4
		if d ** 2 > n: break
		n = testDiv(primfac, n, d)
		d += 2
		if d ** 2 > n: break
		n = testDiv(primfac, n, d)
		d += 4
		if d ** 2 > n: break
		n = testDiv(primfac, n, d)
		d += 6
		if d ** 2 > n: break
		n = testDiv(primfac, n, d)
		d += 2
		if d ** 2 > n: break
		n = testDiv(primfac, n, d)
		d += 6
	if n > 1: primfac += [(n, 1)]
	return primfac
