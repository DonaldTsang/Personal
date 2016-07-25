def testDivide(primfac, n, p):
	counter = 0
	while (n % p) == 0:
		counter += 1
		n //= p
	if counter != 0: primfac += [(p, counter)]
	return n

def primes(n):
	primfac = []
	n = testDivide(primfac, n, 2)
	n = testDivide(primfac, n, 3)
	n = testDivide(primfac, n, 5)
	counter, d = 0, 7
	while d**2 <= n:
		n = testDivide(primfac, n, d)
		d += 4
		if d** 2 > n: break
		n = testDivide(primfac, n, d)
		d += 2
		if d** 2 > n: break
		n = testDivide(primfac, n, d)
		d += 4
		if d** 2 > n: break
		n = testDivide(primfac, n, d)
		d += 2
		if d** 2 > n: break
		n = testDivide(primfac, n, d)
		d += 4
		if d** 2 > n: break
		n = testDivide(primfac, n, d)
		d += 6
		if d** 2 > n: break
		n = testDivide(primfac, n, d)
		d += 2
		if d** 2 > n: break
		n = testDivide(primfac, n, d)
		d += 6
	if n > 1: primfac += [(n, 1)]
	return primfac
