from random import randint

dice = [0, 0, 0]
result = [0, 0, 0]
pairs = ()
def roll():
	global dice, result, pairs
	dice[0], dice[1], dice[2] = randint(1, 6), randint(1, 6), randint(1, 6)
	result = sorted([dice[0], dice[1], dice[2]])
	if result[0] == result[1] == result [2]: pairs = (3, result[0])
	elif result[0] == result[1]: pairs = (2, result[0])
	elif result[1] == result [2]: pairs = (2, result[1])
	else: pairs = (1, 0)

class twister(object):
	def __init__(self, cash):
		self.cash = cash

	def check(self, bet):
		assert isinstance(self.cash, int)
		assert isinstance(bet, int)
		assert self.cash >= bet > 0
		self.cash -= bet
		return self.cash

	def duo_sum(self, bet, pick):
		self.cash = twister.check(self, bet)
		assert isinstance(pick, int)
		assert 2 <= pick <= 12
		roll()
		print("You picked two dice totalling %s, and rolls are %s" % (pick, dice))
		if pick == dice[0] + dice[1]:
			if pick in [2, 12]:
				self.cash += 36 * bet # zero house edge
			elif pick in [3, 11]:
				self.cash += 18 * bet # zero house edge
			elif pick in [4, 10]:
				self.cash += 12 * bet # zero house edge
			elif pick in [5, 9]:
				self.cash += 9 * bet # zero house edge
			elif pick in [6, 8]:
				self.cash += 7 * bet + (bet * 2) // 12
			elif pick == 7:
				self.cash += 6 * bet # zero house edge
		print(self.cash)

	def trio_sum(self, bet, pick):
		self.cash = twister.check(self, bet)
		assert isinstance(pick, int)
		assert 3 <= pick <= 18
		roll()
		print("You picked three dice totaling %s, and rolls are %s" % (pick, dice))
		if pick == dice[0] + dice[1] + dice[2]:
			if pick in [3, 18]:
				self.cash += 216 * bet # zero house edge
			elif pick in [4, 17]:
				self.cash += 72 * bet # zero house edge
			elif pick in [5, 16]:
				self.cash += 36 * bet # zero house edge
			elif pick in [6, 15]:
				self.cash += 21 * bet + (bet * 7) // 12
			elif pick in [7, 14]:
				self.cash += 14 * bet + (bet * 5) // 12
			elif pick in [8, 13]:
				self.cash += 10 * bet + (bet * 3) // 12
			elif pick in [9, 12]:
				self.cash += 8 * bet + (bet * 7) // 12
			elif pick in [10, 11]:
				self.cash += 8 * bet # zero house edge
		print(self.cash)

	def duo_twin(self, bet, pick):
		self.cash = twister.check(self, bet)
		assert pick in ["odd", "even", "mixed"]
		roll()
		print("You picked two dice being %s, and rolls are %s" % (pick, dice))
		if dice[0] % 2 == dice[1] % 2:
			if dice[0] % 2 == 1 and pick == "odd":
				self.cash += 4 * bet # zero house edge
			elif dice[0] % 2 == 0 and pick == "even":
				self.cash += 4 * bet # zero house edge
		elif pick == "mixed":
			self.cash += 2 * bet # zero house edge
		print(self.cash)

	def trio_twin(self, bet, pick):
		self.cash = twister.check(self, bet)
		assert pick in ["odd", "even", "mixed"]
		roll()
		print("You picked three dice being %s, and rolls are %s" % (pick, dice))
		if dice[0] % 2 == dice[1] % 2 == dice[2] % 2:
			if dice[0] % 2 == 1 and pick == "odd":
				self.cash += 8 * bet # zero house edge
			elif dice[0] % 2 == 0 and pick == "even":
				self.cash += 8 # zero house edge
		elif pick == "mixed":
			self.cash += 1 * bet + (bet * 4) // 12
		print(self.cash)

	def duo_dubs(self, bet, pick):
		self.cash = twister.check(self, bet)
		assert isinstance(pick, int)
		assert 0 <= pick <= 6
		roll()
		print("You picked two dice double %ss, and rolls are %s" % (pick, dice))
		if dice[0] == dice[1]:
			if pick == 0:
				self.cash += 6 * bet # zero house edge
			elif dice[0] == pick:
				self.cash += 36 * bet # zero house edge
		print(self.cash)

	def trio_dubs(self, bet, pick):
		self.cash = twister.check(self, bet)
		assert isinstance(pick, int)
		assert 0 <= pick <= 6
		roll()
		print("You picked three dice double %ss, and rolls are %s" % (pick, dice))
		if pairs[0] == 2:
			if pick == 0:
				self.cash += 2 * bet + (bet * 4) // 12
			elif dice[0] == pick:
				self.cash += 14 * bet + (bet * 4) // 12
		print(self.cash)

	def trio_trips(self, bet, pick):
		self.cash = twister.check(self, bet)
		assert isinstance(pick, int)
		assert 0 <= pick <= 6
		roll()
		print("You picked three dice double %ss, and rolls are %s" % (pick, dice))
		if pairs[0] == 3:
			if pick == 0:
				self.cash += 36 * bet # zero house edge
			elif dice[0] == pick:
				self.cash += 216 * bet # zero house edge
		print(self.cash)

	def trio_straight(self, bet, pick): # zero house edge
		self.cash = twister.check(self, bet)
		assert pick in ["lo", "high", "any"]
		roll()
		print("You picked straights, and rolls are %s" % dice)
		if result in [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6]]:
			if result in [[1, 2, 3], [2, 3, 4]] and pick == "lo":
				self.cash += 18 * bet
			elif result in[[3, 4, 5], [4, 5, 6]] and pick == "high":
				self.cash += 18 * bet
			elif pick == "any":
				self.cash += 9 * bet
		print(self.cash)

	def trio_number(self, bet, pick): # zero house edge
		self.cash = twister.check(self, bet)
		assert isinstance(pick, int)
		assert 1 <= pick <= 6
		roll()
		print("You picked %ss, and rolls are %s" % (pick, dice))
		if pairs[1] == pick:
			if pairs[0] == 3:
				self.cash += 9 * bet + (bet * 9) // 12
			elif pairs[0] == 2:
				self.cash += 3 * bet + (bet * 9) // 12
		elif pick in dice:
			self.cash += 2 * bet
		print(self.cash)

	# Need Field Bets and Big/Small a.k.a Hi/Mid/Lo
