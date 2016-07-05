from random import randint, shuffle
def password_gen(total, upcase, lowcase, numbers, others = 0, characters = '+-_=.:/'):
	assert isinstance(total, int)
	assert isinstance(upcase, int)
	assert isinstance(lowcase, int)
	assert isinstance(numbers, int)
	assert isinstance(others, int)
	assert isinstance(characters, str)
	assert total >= ( upcase + lowcase + numbers + others )
	up_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	low_char = 'abcdefghijklmnopqrstuvwxyz'
	num_char = '0123456789'
	characters = characters
	royale = up_char + low_char + num_char + characters
	result = ''
	for i in range(0, upcase):
		result += up_char[randint(0, 25)]
	for i in range(0, lowcase):
		result += low_char[randint(0, 25)]
	for i in range(0, numbers):
		result += num_char[randint(0, 9)]
	for i in range(0, others):
		result += characters[randint(0, len(characters)-1)]
	for i in range(0, total - upcase - lowcase - numbers - others):
		result += royale[randint(0, len(royale)-1)]
	result = list(result)
	shuffle(result)
	return ''.join(result)
