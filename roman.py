def roman_digit(num, one, five, ten):
	assert isinstance(num, int)
	assert 0 <= num < 10
	assert isinstance(one, str)
	assert isinstance(five, str)
	assert isinstance(ten, str)
	if 0 < ( num % 5 ) < 4:
		ones = one * ( num % 5 )
		if num // 5 == 0:
			return ones
		elif num // 5 == 1:
			return five + ones
	elif num % 5 == 4:
		if num // 5 == 0:
			return one + five
		elif num // 5 == 1:
			return one + ten
	elif num % 5 == 0:
		if num // 5 == 0:
			return ''
		elif num // 5 == 1:
			return five

def roman_triples(num):
	assert isinstance(num, int)
	assert 0 <= num < 1000
	if num == 0:
		return '0'
	string = str(num).zfill(3)
	return roman_digit(int(string[0]), 'C', 'D', 'M') + \
		roman_digit(int(string[1]), 'X', 'L', 'C') + \
		roman_digit(int(string[2]), 'I', 'V', 'X')
