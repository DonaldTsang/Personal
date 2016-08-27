#!/usr/bin/python

import re
from textwrap import wrap

# https://github.com/natmchugh/drunken-bishop/blob/master/drunken-bishop.py
# https://github.com/atoponce/keyart/blob/master/keyart

def chop(string, length): # chop string into blocks
	return [string[i:i+length] for i in range(0, len(string), length)]

def trim(string, length, char): # trim padding of a string
	return string.rstrip(char).ljust(length, char)

def insert(string, char, index): # insert string into another string
	return string[:index] + char + string[index:]

def new_line(text, count): # split long string and add newline
	return "\n".join(wrap(text, count))

def multiline():
	print("Enter as many lines of text as needed" + \
		"When done, enter '>' on a line by itself.")
	buffer = []
	while True:
	    line = input()
	    if line == ">": break
	    buffer.append(line)
	return "\n".join(buffer)

def matrix(x):
	return [list(item) for item in list(zip(*x))]

################################################################################

class Codex(object):

	def __init__(self, exp, base, limit, regex, byte_list):
		self.exp = exp # Number of bits contained in a block
		self.base = base # Radix system inside of a block
		self.limit = limit # Number of characters in a block
		self.regex = regex # Regex fullmatch system of a block
		self.byte_list = byte_list # Byte shortening of a block
		self.bound, self.byte = 2 ** self.exp, self.exp // 8

	#        |000000000111111111122222222223333333|
	#        |123456789012345678901234567890123456|
	digit = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" + \
		"abcdefghijklmnopqrstuvwxyz.-:+=^!/*?()[]@%$#"
	#   |33344444444445555555555666666666677777777778|
	#   |78901234567890123456789012345678901234567890|

# This is the same character set as Z85 excluding &<>{}
# It does not includes _,;"'|\~`

	def check(self): # checks integrity of Codex
		assert isinstance(self.base, int), "Error: base not integer"
		assert 56 <= self.base < 96, "Error: base out of range"
		assert isinstance(self.exp, int), "Error: exponent not integer"
		assert self.exp > 0, "Error: xponent not positive"
		assert self.exp % 8 == 0, "Error: exponent not multiple of 8"
		assert isinstance(self.limit, int), "Error: limit not integer"
		assert self.limit > 0, "Error: limit not positive"
		assert isinstance(regex, str), "Error: regex not string"
		assert self.digit[0] == "0", "Error: first digit not zero"

################################################################################

	def en(integer, self): # encode integer into text
		assert isinstance(integer, int), "Error: message not integer"
		assert 0 <= integer < self.bound, "Error: number out of range"
		if integer == 0: return "0" * self.limit
		result=""
		while integer != 0:
			integer, char = divmod(integer, self.base)
			result += self.digit[char]
		return result.ljust(self.limit, "0")

	def de(string, self): # decode text into integer
		assert isinstance(string, str), "Error: message not string"
		assert len(string) <= self.limit, "Error: string too long"
		assert bool(re.fullmatch(self.regex % self.limit, string))
		result, string = 0, string[::-1].lstrip("0")
		for char in string:
			result *= self.base; result += self.digit.index(char)
		assert result < self.bound, "Error: number error"
		return result

	def u2i(string, self): # encode unicode into integer
		if isinstance(string, str): passwd = passwd.encode('utf-8')
		assert isinstance(string, bytes), "Error: password not bytes"
		assert len(string) <= (self.byte), "Error: string too long"
		result, string = 0, string[::-1].lstrip(b'\x00')
		for char in string:
			result *= 256; result += char
		return result

	def i2u(integer, self): # decode integer into unicode
		assert isinstance(integer, int), "Error: number not integer"
		assert 0 <= integer < self.bound, "Error: number out of range"
		if integer == 0: return b"\x00" * self.byte
		result = []
		while integer != 0:
			integer, r = divmod(integer, 256)
			result += [r]
		result += [0] * (self.byte-len(result))
		return bytes(result)

	def block_en(string, self): # encoding unicode into text
		medium = Codex.en(Codex.u2i(string, self), self)
		if len(string) == self.byte: return medium
		return trim(medium, self.byte_list[len(string)], "0")

	def block_de(string, self): # decoding text into unicode
		medium = Codex.i2u(Codex.de(string, self), self)
		if len(string) == self.limit: return medium
		return trim(medium, self.byte_list.index(len(string)), b"\x00")

	def mess_en(string, self): # encode unicode into text
		if isinstance(string, str): string = string.encode('utf-8')
		assert isinstance(string, bytes), "Error: message not bytes"
		string = chop(string, self.byte)
		return "".join([Codex.block_en(steak, self) for steak in string])

	def mess_de(string, self): # decode text into unicode
		assert isinstance(string, str), "Error: message not string"
		string = chop(string, self.limit)
		return b"".join([Codex.block_de(steak, self) for steak in string])

################################################################################

class Code(Codex):

	def __init__(self, exp, shift):
		self.exp = exp # Number of bits contained in a block
		self.shift = shift # Radix system version of a block
		Codex.base, Codex.limit = Code.shifting(self.exp, self.shift)
		Codex.regex, Codex.byte_list = self.dictionary[self.base]
		self.bound, self.byte = 2 ** self.exp, self.exp // 8

	def shifty(exp): # for 160/192/224/256-bits
		assert isinstance(exp, int), "Error: exponent not integer"
		assert exp % 32 == 0, "Error: exponent not multiple of 32"
		exp //= 32
		assert 5 <= exp <= 8, "Error: exponent out of range"
		limit, base = exp * 5 + 1, exp + 68
		base -= 1 if base == 73 else 0
		return base, limit

	def shiftx(exp, shift): # for 256/320/384/448/512-bits
		assert isinstance(exp, int), "Error: exponent not integer"
		assert exp % 64 == 0, "Error: exponent not multiple of 64"
		exp //= 64
		assert isinstance(shift, int), "Error: shift not integer"
		assert 1 <= shift <= 3, "Error: shift out of range"
		assert (3 + shift) <= exp <= 8, "Error: exponent out of range"
		limit, base = exp * 10 + shift, exp + 76 - 4 * shift
		base += 1 if shift == 1 else 0
		base -= 1 if base in [70, 73, 77, 81] else 0
		return base, limit

	def shifting(exp, shift = 0):
		assert isinstance(exp, int), "Error: exponent not integer"
		assert isinstance(shift, int), "Error: shift not integer"
		assert -1 <= shift <= 3, "Error: shift not 0, 1, 2, or 3"
		assert (exp == 128) == (shift == -1), "Error: 128-bit break"
		if exp == 128 and shift == -1: base, limit = 69, 21
		elif shift == 0: base, limit = Code.shifty(exp)
		else: base, limit = Code.shiftx(exp, shift)
		return base, limit

	dictionary = {
		80: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}",
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 14, 16, 17, 18, 19, 
			21, 22, 23, 25, 26, 27, 28, 30, 
			31, 32, 33, 35, 36, 37, 38, 40, 
			41, 42, 44, 45, 46, 47, 49, 50, 
			51, 52, 54, 55, 56, 57, 59, 60, 
			61, 63, 64, 65, 66, 68, 69, 70, 
			71, 73, 74, 75, 76, 78, 79, 80]),
		79: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}", 
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 14, 16, 17, 18, 20, 
			21, 22, 23, 25, 26, 27, 28, 30, 
			31, 32, 33, 35, 36, 37, 39, 40, 
			41, 42, 44, 45, 46, 47, 49, 50, 
			51, 53, 54, 55, 56, 58, 59, 60]),
		78: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}",
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 15, 16, 17, 18, 20, 
			21, 22, 23, 25, 26, 27, 29, 30, 
			31, 32, 34, 35, 36, 37, 39, 40, 
			41, 43, 44, 45, 46, 48, 49, 50]),
		76: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}",
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 15, 16, 17, 18, 20, 
			21, 22, 24, 25, 26, 27, 29, 30, 
			31, 33, 34, 35, 36, 38, 39, 40, 
			41, 43, 44, 45, 47, 48, 49, 50, 
			52, 53, 54, 56, 57, 58, 59, 61, 
			62, 63, 65, 66, 67, 68, 70, 71, 
			72, 73, 75, 76, 77, 79, 80, 81]),
		75: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}",
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 15, 16, 17, 18, 20, 
			21, 22, 24, 25, 26, 27, 29, 30, 
			31, 33, 34, 35, 36, 38, 39, 40, 
			42, 43, 44, 45, 47, 48, 49, 51, 
			52, 53, 54, 56, 57, 58, 60, 61, 
			62, 63, 65, 66, 67, 69, 70, 71]),
		74: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}",
			[0, 2, 3, 4, 6, 7, 8, 10, 
			11, 12, 13, 15, 16, 17, 19, 20, 
			21, 22, 24, 25, 26, 28, 29, 30, 
			31, 33, 34, 35, 37, 38, 39, 40, 
			42, 43, 44, 46, 47, 48, 49, 51, 
			52, 53, 55, 56, 57, 58, 60, 61]),
		72: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}",
			[0, 2, 3, 4, 6, 7, 8, 10, 
			11, 12, 13, 15, 16, 17, 19, 20, 
			21, 23, 24, 25, 26, 28, 29, 30, 
			32, 33, 34, 36, 37, 38, 39, 41, 
			42, 43, 45, 46, 47, 48, 50, 51, 
			52, 54, 55, 56, 58, 59, 60, 61, 
			63, 64, 65, 67, 68, 69, 71, 72, 
			73, 74, 76, 77, 78, 80, 81, 82]),
		71: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}",
			[0, 2, 3, 4, 6, 7, 8, 10, 
			11, 12, 14, 15, 16, 17, 19, 20, 
			21, 23, 24, 25, 27, 28, 29, 30, 
			32, 33, 34, 36, 37, 38, 40, 41, 
			42, 43, 45, 46, 47, 49, 50, 51, 
			53, 54, 55, 56, 58, 59, 60, 62, 
			63, 64, 66, 67, 68, 69, 71, 72]),
		69: ("[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}",
			[0, 2, 3, 4, 6, 7, 8, 10, 
			11, 12, 14, 15, 16, 18, 19, 20, 
			21, 23, 24, 25, 27, 28, 29, 31, 
			32, 33, 35, 36, 37, 38, 40, 41, 
			42, 44, 45, 46, 48, 49, 50, 52, 
			53, 54, 56, 57, 58, 59, 61, 62])
	}

################################################################################

byte = [0, 2, 3, 5, 6, 7, 9, 10,
	11, 13, 14, 15, 17, 18, 19, 21,
	22, 23, 25, 26, 27, 29, 30, 31,
	33, 34, 35, 37, 38, 39, 41, 42,
	43, 45, 46, 47, 49, 50, 51, 53,
	54, 55, 57, 58, 59, 61, 62, 63,
	65, 66, 67, 69, 70, 71, 73, 74]

base63 = Codex(448, 63, 75, "[0-9A-Za-z_]{1,%d}", byte)
base62 = Codex(256, 62, 43, "[0-9A-Za-z]{1,%d}", byte)
base61 = Codex(160, 61, 27, "[0-9A-Za-y]{1,%d}", byte)
base60 = Codex(112, 60, 19, "[0-9A-Za-x]{1,%d}", byte)

################################################################################

import hashlib

def pass_check(passwd):
	if isinstance(passwd, str): passwd = passwd.encode('utf-8')
	assert isinstance(passwd, bytes), "Error: password not bytes"
	sp, bar, space = " ", "||", "   "
	def mid(center, side): return side + center + side
	md5_128 = hashlib.md5(passwd).digest()
	sha_256 = hashlib.sha256(passwd).digest()
	sha_384 = hashlib.sha384(passwd).digest()
	sha_512 = hashlib.sha512(passwd).digest()
	code_128 = Codex.mess_en(md5_128, Code(128, -1))
	code_256 = Codex.mess_en(sha_256, Code(128, -1))
	code_384 = Codex.mess_en(sha_384, Code(128, -1))
	code_512 = Codex.mess_en(sha_512, Code(128, -1))
	code_l = mid(["S H", "H A", "A S", "& H", "M I", "D N", "5 G"], [space])
	code_c = chop(code_256 + code_384 + code_512, 21)
	code_r = mid(chop(code_128, 3), [space])
	code = []
	for i in range(0, 9):
		code += [mid(code_l[i], sp) + mid(code_c[i], bar) + mid(code_r[i], sp)]
	return code

################################################################################

"""
def shiftz(exp):
	exp //= 64
	assert 4 <= exp <= 8
	limit, base = exp * 10 - 1, 98 - exp
	base += 1 if base == 94 else 0 
	return base, limit
"""

################################################################################

def hex_byte_to_bin(hex_byte): # convert hex byte into a string of bits
	assert bool(re.fullmatch("[0-9A-Fa-f]{2}", hex_byte))
	return bin(int(hex_byte, 16))[2:].zfill(8)

def bit_pairs(binary): # convert a word into little-endian bit pairs
	from itertools import islice
	def take(n, iterable): # Return first n items of the iterable as a list
		return list(islice(iterable, n))
	def all_pairs(iterable):
		while True:
			pair = take(2, iterable)
			if not pair: break
			yield "".join(pair)
	return list(all_pairs(iter(binary)))[::-1]

def octo(fingerprint): # convert hexadecimal into octal
	assert bool(re.fullmatch("[0-9A-Fa-f]{64}", fingerprint))
	fingerprint = oct(int(fingerprint, 16))[2:].zfill(86)
	return int(fingerprint[0]), fingerprint[1:]

class Direct(object): # Encode a sense of direction
	def __init__(self, dx, dy): self.dx, self.dy = dx, dy

NW, NE, SW, SE = Direct(-1, -1), Direct(1, -1), Direct(-1, 1), Direct(1, 1)
NNW, NNE, SSW, SSE = Direct(-1, -2), Direct(1, -2), Direct(-1, 2), Direct(1, 2)
WSW, WNW, ESE, ENE = Direct(-2, 1), Direct(-2, -1), Direct(2, 1), Direct(2, -1)

def directions_from_fingerprint(fingerprint): # convert fingerprint into direction
	direction_lookup = {"00": NW, "01": NE, "10": SW, "11": SE}
	for hex_byte in fingerprint.split(":"):
		binary = hex_byte_to_bin(hex_byte)
		# read each bit-pair in each word right-to-left (little endian)
		for bit_pair in bit_pairs(binary):
			direction = direction_lookup[bit_pair]
			yield direction

def directions_from_fingerprint_knight(fingerprint): # convert fingerprint into direction
	direction_lookup = {"0": NNW, "1": NNE, "2": SSW, "3": SSE,
		"4": WSW, "5": WNW, "6": ESE, "7": ENE}
	for character in octo(fingerprint)[1]:
		direction = direction_lookup[character]
		yield direction

################################################################################

# encode start and end positions
coin_start_position, coin_end_position = 20, 21

def coin(value): # Display the ascii representation of a coin
	return {
		# 2 and 3 changed from "o" and "+"
		0: " ", 1: ".", 2: "i",3: "l", 4: "=",
		5: "*", 6: "B", 7: "O", 8: "X", 9: "@",
		10: "%", 11: "&", 12: "#", 13: "/", 14: "^",
		15: "f", 16: "M", 17: "W", 18: "Z", 19: "?",
		coin_start_position: "S",
		coin_end_position: "E",
	}.get(value, "!")

################################################################################

def db_fix(fingerprint): # add colons to fingerprints
	bihex = "[0-9A-Fa-f]{2}"
	if bool(re.fullmatch("(" + bihex + "[:]){0,}" + bihex, fingerprint)):
		return fingerprint
	elif bool(re.fullmatch("(" + bihex + "){1,}", fingerprint)):
		return ":".join(chop(fingerprint, 2))
	else: assert False, "Error: fingerprint is invalid"

################################################################################

class Size(object):
	def __init__(self, x, y, byte):
		self.x, self.y = x, y # bishop starts in the center of the room
		self.byte = byte # the amount of bytes contained in a single db
		self.start_position = (x, y)
		self.room_dimensions = (x * 2 + 1, y * 2 + 1)
		self.border = "+" + "-" * (x * 2 + 1) + "+\n"

	def move(position, direction, self): # returns new position given current condition
		x, y = position
		max_x, max_y = self.x * 2, self.y * 2
		assert 0 <= x <= max_x, "Error: position of x out of range"
		assert 0 <= y <= max_y, "Error: position of y out of range"
		new_x, new_y = x + direction.dx, y + direction.dy
		# the drunk bishop is hindered by the wall
		new_x = 0 if new_x <= 0 else min(new_x, max_x)
		new_y = 0 if new_y <= 0 else min(new_y, max_y)
		return new_x, new_y

	def stumble_around(fingerprint, self):
		from collections import Counter
		room, position = Counter(), self.start_position
		for direction in directions_from_fingerprint(fingerprint):
			position = Size.move(position, direction, self)
			room[position] += 1  # drop coin
		# mark start and end positions
		room[self.start_position] = coin_start_position
		room[position] = coin_end_position
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

	def db(fingerprint, self): # Creates a piece of art base on 32 hex
		room = Size.stumble_around(db_fix(fingerprint), self)
		return Size.display_room(room, self)

	def db_tops(fingerprint, self): # db but without the bottom frame
		room = Size.stumble_around(db_fix(fingerprint), self)
		return Size.display_room(room, self)[:-(self.room_dimensions[0]+3)]

	def db_multiple(fingerprint, self): # Vertically stacked drunken_bishop
		fingerprint = db_fix(fingerprint)
		finger = [i.rstrip(":") for i in chop(fingerprint, self.byte * 3)]
		picture = [Size.db_tops(i, self) for i in finger]
		return "".join(picture) + self.border

	def db_scrape(fingerprint, self): # remove last character of each line
		room = Size.db_multiple(fingerprint, self).split("\n")[:-1]
		return [item[:-1] for item in room]

	def db_merge(list, self):
		output = matrix([Size.db_scrape(item, self) for item in list])
		output = "\n".join(["".join(item)+item[0][0] for item in output])+"\n"
		return output

small, large = Size(8, 4, 16), Size(11, 6, 32)

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
		room[self.start_position_0], room[self.start_position_1] = [coin_start_position] * 2
		room[position_0], room[position_1] = [coin_end_position] * 2
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

	def db_merge(list, self):
		output = matrix([Size.db_scrape(item, self) for item in list])
		output = "\n".join(["".join(item)+item[0][0] for item in output])+"\n"
		return output

night_0, night_1 = Size_knight(7, 7, 6), Size_knight(5, 11, 6)

################################################################################

import hashlib

def db_basic(passwd, num): # creates rectangles based on hashes
	if isinstance(passwd, str): passwd = passwd.encode('utf-8')
	assert isinstance(passwd, bytes), "input not bytes"
	assert num in [1, 2, 3, 4, 6, 8, 9], "Error: num ivalid"
	md5 = hashlib.md5(passwd).hexdigest()
	sha_256 = hashlib.sha256(passwd).hexdigest()
	sha_384 = hashlib.sha384(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	finger, constant = "", 0
	if num == 1: finger = md5
	elif num == 2: finger = sha_256
	elif num == 3: finger = sha_384
	elif num == 4: finger = sha_512
	elif num == 6: finger = sha_256 + sha_512
	elif num == 8: finger = md5 + sha_384 + sha_512
	elif num == 9: finger = sha_256 + sha_384 + sha_512
	if num in [1, 2, 3]: constant = 32
	elif num in [4, 6, 8]: constant = 64
	elif num == 9: constant = 96
	return Size.db_merge(chop(finger, constant), small)

def db_advanced(passwd, num): # creates rectangles based on hashes
	if isinstance(passwd, str): passwd = passwd.encode('utf-8')
	assert isinstance(passwd, bytes), "input not bytes"
	assert num in [1, 2, 3], "Error: num ivalid"
	sha_256 = hashlib.sha256(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	finger = ""
	if num == 1: finger = sha_256
	elif num == 2: finger = sha_512
	elif num == 3: finger = sha_256 + sha_512
	return Size.db_merge(chop(finger, 64), large)

def db_knight(passwd, num, k=0): # creates rectangles based on hashes
	if isinstance(passwd, str): passwd = passwd.encode('utf-8')
	assert isinstance(passwd, bytes), "input not bytes"
	assert num in [1, 2, 3], "Error: num ivalid"
	assert k in [0, 1], "Error: k invalid"
	sha_256 = hashlib.sha256(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	finger = ""
	if num == 1: finger = sha_256
	elif num == 2: finger = sha_512
	elif num == 3: finger = sha_256 + sha_512
	if k == 0: return Size_knight.db_merge(chop(finger, 64), night_0)
	if k == 1: return Size_knight.db_merge(chop(finger, 64), night_1)

################################################################################

def db_combo(passwd):
	if isinstance(passwd, str): passwd = passwd.encode('utf-8')
	assert isinstance(passwd, bytes), "input not bytes"
	md5 = hashlib.md5(passwd).hexdigest()
	sha_256 = hashlib.sha256(passwd).hexdigest()
	sha_384 = hashlib.sha384(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	top, bottom = md5 + sha_384, sha_256 + sha_512
	m5, m11, m17 = "+" + "-" * 5, "+" + "-" * 11, "+" + "-" * 17
	return Size.db_merge(chop(top, 32), small)[:-74] + \
		m17 + m5 + m11 + m11 + m5 + m17 + "+\n" + \
		Size.db_merge(chop(bottom, 64), large)[74:]

def db_tester(passwd):
	if isinstance(passwd, str): passwd = passwd.encode('utf-8')
	assert isinstance(passwd, bytes), "input not bytes"
	sha_256 = hashlib.sha256(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	finger = sha_256 + sha_512
	return Size.db_merge(chop(finger, 64), large) + \
		Size_knight.db_merge(chop(finger, 64), night_0) + \
		Size_knight.db_merge(chop(finger, 64), night_1)

def db_supreme(passwd): # combines base69 and drunken bishop into one picture
	if isinstance(passwd, str): passwd = passwd.encode('utf-8')
	assert isinstance(passwd, bytes), "input not bytes"
	left = hashlib.md5(passwd).hexdigest() + hashlib.sha256(passwd).hexdigest()
	right = hashlib.sha384(passwd).hexdigest()
	mid = chop(hashlib.sha512(passwd).hexdigest(), 64)
	mid_l, mid_r = insert(mid[0], "0" * 32, 32), insert(mid[1], "0" * 32, 32)
	image = db_merge([left, mid_l, mid_r, right], small).split("\n")
	for i in range(0, 9):
		image[i+11] = image[i+11][:19] + pass_check(passwd)[i]+ image[i+11][54:]
	return "\n".join(image)

################################################################################

from random import randrange, shuffle

def passwd_gen(total, upcase, lowcase, numbers, others = 0, chars = ''):
	assert isinstance(total, int) and total > 0
	def checks(n): assert isinstance(n, int) and n >= 0
	checks(upcase); checks(lowcase); checks(numbers); checks(others)
	assert isinstance(chars, str)
	assert total >= ( upcase + lowcase + numbers + others )
	up_char = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	low_char = "abcdefghijklmnopqrstuvwxyz"
	num_char = "0123456789"
	chars = "+-_=.:/" if chars == '' else chars
	royale = up_char + low_char + num_char + chars
	rest = total - upcase - lowcase - numbers - others
	result = ""
	for i in range(upcase): result += up_char[randrange(26)]
	for i in range(lowcase): result += low_char[randrange(26)]
	for i in range(numbers): result += num_char[randrange(10)]
	for i in range(others): result += chars[randrange(len(chars))]
	for i in range(rest): result += royale[randrange(len(royale))]
	result = list(result); shuffle(result); return "".join(result)

################################################################################

from binascii import hexlify

def hex2cjk(x):
	assert isinstance(x, int)
	assert 0x0 <= x <= 0xffff
	if 0x0 <= x <= 0xfff: x-=0x0; x += 0x3400 # Extended A
	elif 0x1000 <= x <= 0x5fff: x-=0x1000; x += 0x4e00 # Unified CJKV
	elif 0x6000 <= x <= 0xffff: x-=0x6000; x += 0x20000 # Extended B
	return chr(x)

def cjk2hex(x):
	assert isinstance(x, str); x = ord(x)
	if 0x3400 <= x <= 0x43ff: x -= 0x3400; x += 0x0 # Extended A
	elif 0x4e00 <= x <= 0x9dff: x-= 0x4e00; x += 0x1000 # Unified CJKV
	elif 0x20000 <= x <= 0x29fff: x-= 0x20000; x += 0x6000 # Extended B
	else: assert False, "Character not correct"
	return x

def cjk_en(byte):
	assert isinstance(byte, bytes)
	if len(byte) % 2 == 1: byte += b"\x00"
	result = ""
	for i in range(0, len(byte), 2): result += hex2cjk(int(hexlify(byte[i:i+2]), 16))
	return result

def cjk_de(string):
	assert isinstance(string, str)
	result = []
	for char in string: x = cjk2hex(char); result += [x >> 8, x & 255]
	return bytes(result)

################################################################################

from math import ceil, log

def calculate_mersenne_primes():
	# Returns all the mersenne primes with less than 500 digits.
	mersenne_prime_exponents = [
		2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279]
	primes = []
	for exp in mersenne_prime_exponents:
		prime = 1  << exp
		prime -= 1; primes.append(prime)
	return primes

def calculate_thabit_primes():
	thabit_prime_exponents = [
		0, 1, 2, 3, 4, 6, 7, 11, 18, 34, 38, 43, 55, 64, 76, 94, 103, 
			143, 206, 216, 306, 324, 391, 458, 470, 827, 1274]
	primes = []
	for exp in thabit_prime_exponents:
		prime = 3  << exp
		prime -= 1; primes.append(prime)
	return primes

SMALLEST_PRIMES = [
	(2**4 + 1), (2**5 + 5), (2**6 + 3),
	(2**7 + 3), (2**8 + 1), (2**10 + 7),
	(2**12 + 3), (2**14 + 27), (2**16 + 1),
	(2**20 + 7), (2**24 + 43), (2**28 + 3),
	(2**32 + 15), (2**40 + 15), (2**48 + 21),
	(2**56 + 81), (2**64 + 13), (2**80 + 13),
	(2**96 + 61), (2**112 + 25), (2**128 + 51),
	(2**160 + 7), (2**192 + 133), (2**224 + 735),
	(2**256 + 297), (2**320 + 27), (2**384 + 231),
	(2**448 + 211), (2**512 + 75), (2**640 + 115),
	(2**768 + 183), (2**896 + 993), (2**1024 + 643)]
STANDARD_PRIMES = SMALLEST_PRIMES
STANDARD_PRIMES.sort()

def get_large_enough_prime(batch):
	# Returns a prime number that is greater all the numbers in the batch.
	# build a list of primes
	primes = STANDARD_PRIMES
	# find a prime that is greater than all the numbers in the batch
	for prime in primes:
		numbers_greater_than_prime = [i for i in batch if i > prime]
		if len(numbers_greater_than_prime) == 0: return prime
	return None

################################################################################

def egcd(a, b):
	if a == 0: return (b, 0, 1)
	else:
		g, y, x = egcd(b % a, a)
		return g, x - (b // a) * y, y

def xgcd(b, n):
	x0, x1, y0, y1 = 1, 0, 0, 1
	while n != 0:
		(q, n), b = divmod(b, n), n
		x0, x1, y0, y1 = x1, x0 - q * x1, y1, y0 - q * y1
	return  b, x0, y0

def mod_inv(k, prime):
	k %= prime; k *= -1 if k < 0 else 1
	return (prime + egcd(prime, k)[2]) % prime

################################################################################

from random import randrange

def random_polynomial(degree, intercept, upper_bound):
	# Generates a random polynomial with positive coefficients.
	if degree < 0: raise ValueError('Degree must be non-negative.')
	coefficients = [intercept]
	for i in range(degree):
		random_coeff = randrange(0, upper_bound)
		coefficients.append(random_coeff)
	return coefficients

def get_polynomial_points(coefficients, num_points, prime):
	# Calculates the first n polynomial points.
	# [ (1, f(1)), (2, f(2)), ... (n, f(n)) ]
	points = []
	for x in range(1, num_points+1):
		# start with x=1 and calculate the value of y
		y = coefficients[0]
		# calculate each term and add it to y, using modular math
		for i in range(1, len(coefficients)):
			exponentiation = (x**i) % prime
			term = (coefficients[i] * exponentiation) % prime
			y += term; y %= prime
		# add the point to the list of points
		points.append((x, y))
	return points

def modular_lagrange_interpolation(x, points, prime):
	# break the points up into lists of x and y values
	x_values, y_values = zip(*points)
	# initialize f(x) and begin the calculation: f(x) = SUM( y_i * l_i(x) )
	f_x = 0
	for i in range(len(points)):
		# evaluate the lagrange basis polynomial l_i(x)
		numerator, denominator = 1, 1
		for j in range(len(points)):
			# don't compute a polynomial fraction if i equals j
			if i == j: continue
			# compute a fraction & update the existing numerator + denominator
			numerator = (numerator * (x - x_values[j])) % prime
			denominator = (denominator * (x_values[i] - x_values[j])) % prime
		# get the polynomial from the numerator + denominator mod inverse
		lagrange_polynomial = numerator * mod_inv(denominator, prime)
		# multiply the current y & the evaluated polynomial & add it to f(x)
		f_x = (prime + f_x + (y_values[i] * lagrange_polynomial)) % prime
	return f_x

################################################################################

def int_to_charset(val, charset):
	# Turn a non-negative integer into a string.
	if not val >= 0: raise ValueError('"val" must be a non-negative integer')
	if val == 0: return charset[0]
	output = ""
	while val > 0:
		val, digit = divmod(val, len(charset))
		output += charset[digit]
	# reverse the characters in the output and return
	return output[::-1]

def int_to_charset_reverse(val, charset): return int_to_charset(val, charset)[::-1]

def charset_to_int(s, charset):
	# Turn a string into a non-negative integer.
	output = 0
	for char in s: output *= len(charset); output += charset.index(char)
	return output

def charset_reverse_to_int(s, charset): return charset_to_int(s[::-1], charset)

################################################################################

def secret_int_to_points(secret_int, point_threshold, num_points, prime=None):
	# Split a secret integer into shares (pair of integers or x,y coords).
	# Sample points of a random polynomial with y intercept equal to secret int.
	if point_threshold < 2:
		raise ValueError("Threshold must be >= 2.")
	if point_threshold > num_points:
		raise ValueError("Threshold must be < the total number of points.")
	if not prime:
		prime = get_large_enough_prime([secret_int, num_points])
		if not prime:
			raise ValueError("Secret is too long for share calculation!")
	coefficients = random_polynomial(point_threshold-1, secret_int, prime)
	points = get_polynomial_points(coefficients, num_points, prime)
	return points

def points_to_secret_int(points, prime=None):
	# Join int points into a secret int.
	# Get the intercept of a random polynomial defined by the given points.

	if not isinstance(points, list):
		raise ValueError("Points must be in list form.")
	for point in points:
		if not isinstance(point, tuple) and len(point) == 2:
			raise ValueError("Each point must be a tuple of two values.")
		if not (isinstance(point[0], int) and isinstance(point[1], int)):
			raise ValueError("Each value in the point must be an int.")
	x_values, y_values = zip(*points)
	if not prime:
		prime = get_large_enough_prime(y_values)
		if not prime:
			raise ValueError("Error! Point is too large for share calculation!")
	free_coefficient = modular_lagrange_interpolation(0, points, prime)
	secret_int = free_coefficient  # the secret int is the free coefficient
	return secret_int

def point_to_share_str(point, n, char_count, charset, num_of_0):
	# Convert a point (a tuple of two integers) into a share string - that is,
	# a representation of the point that uses the charset provided.
	# point should be in the format (1, 4938573982723...)
	if '~' in charset:
		raise ValueError(
			'The character "~" cannot be in the supplied charset.')
	if not (isinstance(point, tuple) and len(point) == 2 and
			isinstance(point[0], int) and isinstance(point[1], int)):
		raise ValueError(
			'Point format is invalid. Must be a pair of integers.')
	x, y = point
	x_str, y_str = int_to_charset(x,  b16), int_to_charset(y, charset)
	share_str = x_str.rjust(n, charset[0]) + '~' + y_str.rjust(char_count, charset[0])
	if num_of_0 != 0:
		share_str += '~' + int_to_charset(num_of_0, b16)
	return share_str

def share_str_to_point(share_str, charset):
	# Convert a share string to a point (a tuple of integers).
	# share should be in the format "01~D051080DE7..."
	if '~' in charset:
		raise ValueError('The character "~" cannot be in the charset.')
	if not isinstance(share_str, str):
		raise ValueError('Share format is invalid.')
	num_of_0 = None
	if share_str.count('~') == 1: x_str, y_str = share_str.split('~')
	elif share_str.count('~') == 2: x_str, y_str, num_of_0 = share_str.split('~')
	else: raise ValueError('Share format is invalid.')
	if (set(x_str) - set(charset)) or (set(y_str) - set(charset)):
		raise ValueError("Share has characters that aren't in the charset.")
	x, y = charset_to_int(x_str, b16), charset_to_int(y_str, charset)
	if num_of_0: num_of_0 = charset_to_int(num_of_0, b16)
	return (x, y), num_of_0

""" Creates a secret sharer, which can convert from a secret string to a
	list of shares and vice versa. Splitter is initialized with
	char_set of the secrets and char_set of the shares that
	it expects to be dealing with."""

class SS():
	def __init__(self, secret_charset, share_charset):
		self.secret_charset = secret_charset
		self.share_charset = share_charset

	def split(self, secret_str, share_threshold, num_shares):
		num_of_0 = 0
		for secret_char in secret_str:
			if secret_char == self.secret_charset[0]: num_of_0 += 1
			else: break
		secret_int = charset_to_int(secret_str, self.secret_charset)
		points = secret_int_to_points(secret_int, share_threshold, num_shares)
		maxim = 0
		for point in points:
			if point[1] > maxim: maxim = point[1]
		char_count = ceil(log(maxim, len(self.share_charset)))
		n = ceil(log(num_shares, len(self.share_charset)))
		shares = []
		for point in points:
			share_str = point_to_share_str(
				point, n, char_count, self.share_charset, num_of_0)
			shares.append(share_str)
		return shares

	def recover(self, shares):
		num_of_0 = None
		points = []
		for share in shares:
			point, num_of_0 = share_str_to_point(
				share, self.share_charset)
			points.append(point)
		secret_int = points_to_secret_int(points)
		secret_str = int_to_charset(secret_int, self.secret_charset)
		if num_of_0:
			leading_0 = self.secret_charset[0] * num_of_0
			secret_str = leading_0 + secret_str
		return secret_str

from binascii import hexlify, unhexlify

def split_str(secret_str, share_charset, share_threshold, num_shares):
	if isinstance(secret_str, str): secret_str = secret_str.encode('utf-8')
	secret_str = hexlify(secret_str).decode('utf-8').upper()
	SS_class = SS(b16, share_charset)
	return SS.split(SS_class, secret_str, share_threshold, num_shares)

def recover_str(shares, share_charset, mode='str'): # need to fix
	assert mode in ['str', 'bytes']
	SS_class = SS(b16, share_charset)
	secret_str = unhexlify(recover(SS_class, shares))
	if mode == 'str': return secret_str.decode('utf-8')
	elif mode == 'bytes': return secret_str

b16 = "0123456789ABCDEF"
b32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + \
	"0123456789+/"
url = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + \
	"0123456789-_"
unix = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" + \
	"abcdefghijklmnopqrstuvwxyz"
xxcode = "+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"  + \
	"abcdefghijklmnopqrstuvwxyz"
uucode = " !\"#$%&'()*+,-./0123456789:;<=>?@" + \
	"ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_"
binhex = "!\"#$%&'()*+,-012345689@ABCDEFGHIJKLMNPQRSTUVXYZ[`" + \
	"abcdefhijklmpqr"
options = [b16, b32, b64, url, unix, xxcode, uucode, binhex]

################################################################################

import base64, codecs
from random import SystemRandom

table = {
256: 189, 320: 197, 384: 317,
448: 203, 512: 569, 640: 305,
768: 825, 896: 213, 1024: 105}

x = 256
prime, hex_len = 2 ** x - table[x], x // 8
b64_len = ((hex_len - 1) // 3 + 1) * 4

def random(): return SystemRandom().randrange(prime)

def split_ints(secret):
	result = []
	working = None
	byte_object = None
	try: byte_object = bytes(secret, "utf8")
	except: byte_object = bytes(secret)
	text = codecs.encode(byte_object, 'hex_codec').decode('utf8') + \
		"00"*(hex_len - (len(byte_object) % hex_len))
	for i in range(0, int(len(text)/(hex_len*2))):
		result.append(int(text[i*hex_len*2:(i+1)*hex_len*2], 16))
	return result

def merge_ints(secrets):
	result = ""
	for secret in secrets:
		hex_data = hex(secret)[2:]
		result += hex_data.rjust(hex_len * 2, "0")
	byte_object = None
	try:
		byte_object = bytes(result, "utf8")
		return codecs.decode(byte_object, 'hex_codec').decode('utf8').rstrip("\00\x00")
	except:
		byte_object = bytes(result)
		return codecs.decode(byte_object, 'hex_codec').rstrip("\00\x00")

def evaluate_polynomial(coefficients, value):
	result = 0
	for coefficient in reversed(coefficients):
		result = (result * value + coefficient) % prime
	return result

def to_base64(number):
	tmp = hex(number)[2:].rjust(hex_len * 2, "0")
	try: tmp = bytes(tmp, "utf8")
	except: tmp = bytes(tmp)
	result = str(base64.urlsafe_b64encode(b'\00'*((hex_len * 2) - len(tmp)) + \
		codecs.decode(tmp, 'hex_codec')).decode('utf8'))
	return result

def from_base64(number):
	byte_number = number
	try: byte_number = bytes(byte_number, "utf8")
	except: byte_number = bytes(byte_number)
	tmp = base64.urlsafe_b64decode(byte_number)
	try: tmp = bytes(tmp, "utf8")
	except: tmp = bytes(tmp)
	return int(codecs.encode(tmp, 'hex_codec'), 16)

def create(minimum, shares, raw):
	def magic(numbers):
		value = random()
		while value in numbers: value = random()
		numbers.append(value)
		return value, numbers
	if (shares < minimum): print("error")
	secret, numbers, polynomial = split_ints(raw), [0], []
	for i in range(0, len(secret)):
		polynomial.append([secret[i]])
		for j in range(1, minimum):
			value, numbers = magic(numbers)
			polynomial[i].append(value)
	result = [""]*shares
	for i in range(0, shares):
		for j in range(0, len(secret)):
			value, numbers = magic(numbers)
			y = evaluate_polynomial(polynomial[j], value)
			result[i] += to_base64(value) + to_base64(y)
	return result

def combine(shares):
	secrets = []
	for index,share in enumerate(shares):
		if len(share) % (b64_len * 2) != 0:
			return "Error"
		count = int(len(share) / (b64_len * 2))
		secrets.append([])
		for i in range(0, count):
			cshare = share[i*b64_len*2:(i+1)*b64_len*2]
			secrets[index].append([from_base64(cshare[0:b64_len]), \
				from_base64(cshare[b64_len:b64_len*2])])
	secret = [0] * len(secrets[0])
	for part_index,part in enumerate(secret):
		for share_index,share in enumerate(secrets):
			origin, originy = share[part_index][0:2]
			numerator, denominator = 1, 1
			for product_index,product in enumerate(secrets):
				if product_index != share_index:
					current = product[part_index][0]
					numerator = (numerator * (-1 * current)) % prime
					denominator = (denominator * (origin - current)) % prime
			working = ((originy * numerator * mod_inv(denominator)) + prime)
			secret[part_index] = (secret[part_index] + working) % prime
	return merge_ints(secret)
