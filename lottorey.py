from random import randint, randrange

def lotto(start, end, pick):
	assert isinstance(start, int), "starting number not integer"
	assert isinstance(end, int), "ending number not integer"
	assert end >= start, "starting and ending numbers should swap"
	if isinstance(pick, int): return lotto(start, end, [pick])
	assert isinstance(pick, list), "pick should be list"
	for i in pick: assert isinstance(i, int), "i should be integer"
	count = 0
	for i in pick: count += i
	assert count <= (end - start + 1), "too many numbers to pick"
	cage = list(range(start, end + 1))
	result = []
	for i in pick:
		result_i = []
		for j in range(i):
			result_i += [cage.pop(randrange(len(cage)))]
		result += [sorted(result_i)]
	return result

def roll(start, end, pick):
	assert isinstance(start, int), "starting number not integer"
	assert isinstance(end, int), "ending number not integer"
	assert end >= start, "starting and ending numbers should swap"
	if isinstance(pick, int): return lotto(start, end, [pick])
	assert isinstance(pick, list), "pick should be list"
	for i in pick: assert isinstance(i, int), "i should be integer"
	result = []
	for i in pick:
		result_i = []
		for j in range(i):
			result_i += [randint(start, end)]
		result += [result_i]
	return result
