def zeckendorf(n):
	if n == 0 : return [0]
	fib, dig = [2,1], []
	while fib[0] < n: fib[0:0] = [sum(fib[:2])]
	for f in fib:
		if f <= n: dig += [1]; n -= f
		else: dig += [0]
	result = dig if dig[0] else dig[1:]
	return str(result)[1:-1].replace(", ", "")
