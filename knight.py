import re

def octo(fingerprint): # convert hexadecimal into octal
	assert bool(re.fullmatch("[0-9A-Fa-f]{64}", fingerprint))
	fingerprint = oct(int(fingerprint, 16))[2:].zfill(86)
	return int(fingerprint[0]), fingerprint[1:]

################################################################################

class Direct(object): # Encode a sense of direction
	def __init__(self, dx, dy):
		self.dx, self.dy = dx, dy

NNW, NNE, SSW, SSE = Direct(-1, -2), Direct(1, -2), Direct(-1, 2), Direct(1, 2)
WSW, WNW, ESE, ENE = Direct(-2, 1), Direct(-2, -1), Direct(2, 1), Direct(2, -1)

def directions_from_fingerprint_knight(fingerprint): # convert fingerprint into direction
	direction_lookup = {"0": NNW, "1": NNE, "2": SSW, "3": SSE,
		"4": WSW, "5": WNW, "6": ESE, "7": ENE}
	for character in octo(fingerprint)[1]:
		direction = direction_lookup[character]
		yield direction

################################################################################

# encode start and end positions
coin_value_start_position, coin_value_end_position = 20, 21

def coin(value): # Display the ascii representation of a coin
	return {
		# 2 and 3 changed from "o" and "+"
		0: " ", 1: ".", 2: "M",3: "W", 4: "=",
		5: "*", 6: "B", 7: "O", 8: "X", 9: "@",
		10: "%", 11: "&", 12: "#", 13: "/", 14: "^",
		15: "f", 16: "i", 17: "l", 18: "Z", 19: "?",
		coin_value_start_position: "S",
		coin_value_end_position: "E",
	}.get(value, "!")

################################################################################

def chop(string, length): # chop string into blocks
	return [string[i:i+length] for i in range(0, len(string), length)]

################################################################################

class Size_knight(object):
	def __init__(self, a, b, c):
		self.a, self.b, self.c = a, b, c # bishop starts in the center of the room
		self.start_position_0, self.start_position_1 = (a, c), (a + b + 1, c)
		self.room_dimensions = (2 * a + b + 2, 2 * c + 1)
		self.border = "+" + "-" * self.room_dimensions[0] + "+\n"

	def move(position, direction, self): # returns new position given current condition
		x, y = position
		max_x, max_y = self.room_dimensions[0] - 1, self.room_dimensions[1] - 1
		assert 0 <= x <= max_x, "Error: position of x out of range"
		assert 0 <= y <= max_y, "Error: position of y out of range"
		new_x, new_y = x + direction.dx, y + direction.dy
		# the drunk bishop is hindered by the wall
		new_x = 0 if new_x <= 0 else min(new_x, max_x)
		new_y = 0 if new_y <= 0 else min(new_y, max_y)
		return new_x, new_y

	def stumble_around(fingerprint, self):
		from collections import Counter
		room = Counter()
		position_0, position_1 = self.start_position_0, self.start_position_1
		ticker = octo(fingerprint)[0]
		for direction in directions_from_fingerprint_knight(fingerprint):
			if ticker == 0:
				position_0 = Size_knight.move(position_0, direction, self)
				room[position_0] += 1  # drop coin
				ticker = 1
			elif ticker == 1:
				position_1 = Size_knight.move(position_1, direction, self)
				room[position_1] += 1  # drop coin
				ticker = 0
		# mark start and end positions
		room[self.start_position_0], room[self.start_position_1] = [coin_value_start_position] * 2
		room[position_0], room[position_1] = [coin_value_end_position] * 2
		return room

	def display_room(room, self):
		X, Y = self.room_dimensions
		def room_as_strings():
			yield self.border
			for y in range(Y):
				yield "|"
				for x in range(X):
					yield coin(room[(x,y)])
				yield "|\n"
			yield self.border
		return "".join(room_as_strings())

	def db(fingerprint, self):
		room = Size_knight.stumble_around(fingerprint, self)
		return Size_knight.display_room(room, self)

	def db_tops(fingerprint, self): # db but without the bottom frame
		room = Size_knight.stumble_around(fingerprint, self)
		return Size_knight.display_room(room, self)[:-(self.room_dimensions[0]+3)]

	def db_multiple(fingerprint, self): # Vertically stacked drunken_bishop
		finger = [i for i in chop(fingerprint, 64)]
		picture = [Size_knight.db_tops(i, self) for i in finger]
		return "".join(picture) + self.border

	def db_scrape(fingerprint, self): # remove last character of each line
		room = Size_knight.db_multiple(fingerprint, self).split("\n")[:-1]
		return [item[:-1] for item in room]

	def db_merge(list, self): # combine multiple vertical ascii frames
		super_list = [Size_knight.db_scrape(item, self) for item in list]
		output = [""] * len(super_list[0])
		for y in range(len(super_list[0])):
			for x in range(len(super_list)):
				output[y] += super_list[x][y]
			output[y] += output[y][0]
		return "\n".join(output) + "\n"
