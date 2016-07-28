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

ping_pong = []
def roll():
	global ping_pong
	ping_pong  = lotto(1, 25, 5)

class Pick5(object):
		def __init__(self, cash):
		self.cash = cash

	def check(self, bet):
		assert isinstance(self.cash, int)
		assert isinstance(bet, int)
		assert self.cash >= bet > 0
		self.cash -= bet
		return self.cash
	
	def picking(self, bet, pick): # too hard to make it zero house edge
		self.cash = Pick5.check(self, bet)
		assert isinstance(pick, list)
		for item in pick:
			assert isinstance(itme, int)
			assert 0 < item <= 25
		for i in range(0, 5):
			for j in range(0, i):
				assert pick[i] != pick[j]
		roll()
		print("You picked %s, and the results are %s" % (pick, ping_pong))
		counter = 0
		for i in ping_pong:
			for j in pick:
				if i == j:
					counter += 1
		if counter == 5:
			self.cash += 16 * bet
		elif counter == 4:
			self.cash += 8 * bet
		elif counter == 3:
			self.cash += 3 * bet + (bet * 9) // 12
		elif counter == 2:
			self.cash += 1 * bet + (bet * 10) // 12
		elif counter == 1:
			self.cash += 1 * bet
		print(self.cash)
