def pythagorean_triples(m, n):
	assert isinstance(m, int), "first number not integer"
	assert isinstance(n, int), "second number not integer"
	assert m > n, "first number smaller than second number"
	return m ** 2 - n ** 2, 2 * m * n, m ** 2 + n ** 2
