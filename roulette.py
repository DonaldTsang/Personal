from random import randint

ball = 0
def roll():
	global ball
	ball = randint(0, 37)

def num(ball):
	assert isinstance(ball, int)
	assert 0 <= ball <= 37
	if ball == 37: return "00"
	else: return str(ball)

class roulette(object):
	def __init__(self, cash):
		self.cash = cash

	def check(self, bet):
		assert isinstance(self.cash, int)
		assert isinstance(bet, int)
		assert self.cash >= bet > 0
		self.cash -= bet

	def num(self, bet, pick): # zero house edge
		self.cash = roulette.check(self, bet)
		assert isinstance(pick, int)
		assert 0 <= pick <= 37
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball == pick:
			self.cash += 38 * bet
		print(self.cash)

	def zero(self, bet): # zero house edge
		self.cash = roulette.check(self, bet)
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball in [0, 37]:
			self.cash += 19 * bet
		print(self.cash)

	def hilo(self, bet, pick):
		self.cash = roulette.check(self, bet)
		assert pick in ["hi", "lo"]
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball in [0, 37]:
			pass
		elif 0 < ball <= 18 and pick == "lo":
			self.cash += 2 * bet + (bet * 1) // 12
		elif 18 < ball <= 36 and pick == "hi":
			self.cash += 2 * bet + (bet * 1) // 12
		print(self.cash)

	def twin(self, bet, pick):
		self.cash = roulette.check(self, bet)
		assert pick in ["odd", "even"]
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball in [0, 37]:
			pass
		elif ball % 2 == 1 and pick == "odd":
			self.cash += 2 * bet + (bet * 1) // 12
		elif ball % 2 == 0 and pick == "even":
			self.cash += 2 * bet + (bet * 1) // 12
		print(self.cash)

	def dozen(self, bet, pick): # zero house edge
		self.cash = roulette.check(self, bet)
		assert pick in ["1st", "2nd", "3rd"]
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball in [0, 37]:
			pass
		elif 0 < ball <= 12 and pick == "1st":
			self.cash += bet * 3 + (bet * 2) // 12
		elif 12 < ball <= 24 and pick == "2nd":
			self.cash += bet * 3 + (bet * 2) // 12
		elif 24 < ball <= 36 and pick == "3rd":
			self.cash += bet * 3 + (bet * 2) // 12
		print(self.cash)

	def lines(self, bet, pick): # zero house edge
		self.cash = roulette.check(self, bet)
		assert pick in ["1st", "2nd", "3rd"]
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball in [0, 37]:
			pass
		elif ball % 3 == 1 and pick == "1st":
			self.cash += bet * 3 + (bet * 2) // 12
		elif ball % 3 == 2 and pick == "2nd":
			self.cash += bet * 3 + (bet * 2) // 12
		elif ball % 3 == 3 and pick == "3rd":
			self.cash += bet * 3 + (bet * 2) // 12
		print(self.cash)

	def sexies(self, bet, pick):
		self.cash = roulette.check(self, bet)
		assert pick in ["1st", "2nd", "3rd", "4th", "5th", "6th"]
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball in [0, 37]:
			pass
		elif 0 < ball <= 6 and pick == "1st":
			self.cash += bet * 6 + (bet * 4) // 12
		elif 6 < ball <= 12 and pick == "2nd":
			self.cash += bet * 6 + (bet * 4) // 12
		elif 12 < ball <= 18 and pick == "3rd":
			self.cash += bet * 6 + (bet * 4) // 12
		elif 18 < ball <= 24 and pick == "4th":
			self.cash += bet * 6 + (bet * 4) // 12
		elif 24 < ball <= 30 and pick == "5th":
			self.cash += bet * 6 + (bet * 4) // 12
		elif 30 < ball <= 36 and pick == "6th":
			self.cash += bet * 6 + (bet * 4) // 12
		print(self.cash)

	def column(self, bet, pick):
		self.cash = roulette.check(self, bet)
		assert pick in ["1st", "2nd", "3rd", "4th", "5th", "6th"]
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball in [0, 37]:
			pass
		elif ball % 6 == 1 and pick == "1st":
			self.cash += bet * 3 + (bet * 2) // 12
		elif ball % 6 == 2 and pick == "2nd":
			self.cash += bet * 3 + (bet * 2) // 12
		elif ball % 6 == 3 and pick == "3rd":
			self.cash += bet * 3 + (bet * 2) // 12
		elif ball % 6 == 4 and pick == "4th":
			self.cash += bet * 3 + (bet * 2) // 12
		elif ball % 6 == 5 and pick == "5th":
			self.cash += bet * 3 + (bet * 2) // 12
		elif ball % 6 == 0 and pick == "6th":
			self.cash += bet * 3 + (bet * 2) // 12

	def colours(self, bet, pick):
		self.cash = roulette.check(self, bet)
		assert pick in ["red", "blue", "teal", "purple",
			"green", "orange", "yellow", "pink"]
		roll()
		print("You picked %s, and ball lands on %s" % (pick, num(ball)))
		if ball in [25, 10, 27, 37, 1, 13, 36] and pick == "red":
			self.cash += bet * 5 + (bet * 5) // 12
		elif ball in [24, 3, 15, 34, 22] and pick == "blue":
			self.cash += bet * 7 + (bet * 7) // 12
		elif ball in [5, 17, 32] and pick == "teal":
			self.cash += bet * 12 + (bet * 8) // 12 # zero house edge
		elif ball in [20, 7, 11, 30] and pick == "purple":
			self.cash += bet * 9 + (bet * 6) // 12 # zero house edge
		elif ball in [26, 9, 28, 0, 2, 14, 35] and pick == "green":
			self.cash += bet * 5 + (bet * 5) // 12
		elif ball in [23, 4, 16, 33, 21] and pick == "orange":
			self.cash += bet * 7 + (bet * 7) // 12
		elif ball in [6, 18, 31] and pick == "yellow":
			self.cash += bet * 12 + (bet * 8) // 12 # zero house edge
		elif ball in [19, 8, 12, 29] and pick == "pink":
			self.cash += bet * 9 + (bet * 6) // 12 # zero house edge
		print(self.cash)
