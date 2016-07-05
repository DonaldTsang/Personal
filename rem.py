def rem(n, a, b):
	m = n
	while n > ((1 << a) - 1):
		m = 0
		while n != 0:
			m += n & ((1 << a) - 1)
			n >>= a
			n *= b
		n = m
	if m + b >= (1 << a):
		return m + b - (1 << a)
	return m
