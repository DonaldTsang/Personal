#!/usr/bin/python

import re

def chop(string, length): # chop string into blocks
	return [string[i:i+length] for i in range(0, len(string), length)]

def trim(string, length, char): # trim padding of a string
	return string.rstrip(char).ljust(length, char)

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
			result *= self.base
			result += self.digit.index(char)
		assert result < self.bound, "Error: number error"
		return result

	def u2i(string, self): # encode unicode into integer
		if isinstance(string, str): passwd = passwd.encode('utf-8')
		assert isinstance(string, bytes), "Error: password not bytes"
		assert len(string) <= (self.byte), "Error: string too long"
		result, string = 0, string[::-1].lstrip(b'\x00')
		for char in string:
			result *= 256
			result += char
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

################################################################################

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

from textwrap import wrap

def new_line(text, count): # split long string and add newline
	return "\n".join(wrap(text, count))

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

import itertools
from collections import Counter

# the bishop starts in the center of the room
start_position = (8, 4) # this is 128-bit, 256-bit should be (11, 6) or (12, 6)
room_dimensions = (start_position[0] * 2 + 1, start_position[1] * 2 + 1)

# encode start and end positions
coin_value_start_position, coin_value_end_position = 15, 16

border = "+" + "-" * room_dimensions[0] + "+\n"

def hex_byte_to_binary(hex_byte): # convert hex byte into a string of bits
	assert len(hex_byte) == 2
	return bin(int(hex_byte, 16))[2:].zfill(8)

def bit_pairs(binary): # convert a word into bit pairs little-endian style
	def take(n, iterable): # Return first n items of the iterable as a list
		return list(itertools.islice(iterable, n))
	def all_pairs(iterable):
		while True:
			pair = take(2, iterable)
			if not pair: break
			yield "".join(pair)
	return list(all_pairs(iter(binary)))[::-1]

################################################################################

class Direction(object): # Encode a sense of direction
	def __init__(self, dx, dy):
		self.dx, self.dy = dx, dy

NW, NE, SW, SE = Direction(-1, -1), Direction(1, -1), Direction(-1, 1), Direction(1, 1)

def directions_from_fingerprint(fingerprint): # convert fingerprint into direction
	direction_lookup = {"00": NW, "01": NE, "10": SW, "11": SE}
	for hex_byte in fingerprint.split(":"):
		binary = hex_byte_to_binary(hex_byte)
		# read each bit-pair in each word right-to-left (little endian)
		for bit_pair in bit_pairs(binary):
			direction = direction_lookup[bit_pair]
			yield direction

def move(position, direction): # returns new position given current condition
	x, y = position
	MAX_X = room_dimensions[0] - 1
	MAX_Y = room_dimensions[1] - 1
	assert 0 <= x <= MAX_X, "Error: position of x out of range"
	assert 0 <= y <= MAX_Y, "Error: position of y out of range"
	new_x, new_y = x + direction.dx, y + direction.dy
	# the drunk bishop is hindered by the wall
	new_x = 0 if new_x <= 0 else min(new_x, MAX_X)
	new_y = 0 if new_y <= 0 else min(new_y, MAX_Y)
	return new_x, new_y

def stumble_around(fingerprint):
	room, position = Counter(), start_position
	for direction in directions_from_fingerprint(fingerprint):
		position = move(position, direction)
		room[position] += 1  # drop coin
	# mark start and end positions
	room[start_position] = coin_value_start_position
	room[position] = coin_value_end_position
	return room

def coin(value): # Display the ascii representation of a coin
	return {
		0: " ", 1: ".", 2: "o", 3: "+", 4: "=",
		5: "*", 6: "B", 7: "O", 8: "X", 9: "@",
		10: "%", 11: "&", 12: "#", 13: "/", 14: "^",
		coin_value_start_position: "S",
		coin_value_end_position: "E",
	}.get(value, "!")

def display_room(room):
	X, Y = room_dimensions
	def room_as_strings():
		yield border
		for y in range(Y):
			yield "|"
			for x in range(X):
				yield coin(room[(x,y)])
			yield "|\n"
		yield border
	return "".join(room_as_strings())

################################################################################

import re

def db_fix(fingerprint): # add colons to fingerprints
	bihex = "[0-9A-Fa-f]{2}"
	if bool(re.fullmatch("(" + bihex + "[:]){0,}" + bihex, fingerprint)):
		return fingerprint
	elif bool(re.fullmatch("(" + bihex + "){1,}", fingerprint)):
		return ":".join(chop(fingerprint, 2))
	else: assert False, "Error: fingerprint is invalid"

def db(fingerprint): # Creates a piece of art base on 32 hex
	room = stumble_around(db_fix(fingerprint))
	return display_room(room)

def db_tops(fingerprint): # db but without the bottom frame
	room = stumble_around(db_fix(fingerprint))
	return display_room(room)[:-(room_dimensions[0]+3)]

def chop(string, length): # chop string into blocks
	return [string[i:i+length] for i in range(0, len(string), length)]

def db_multiple(fingerprint): # Vertically stacked drunken_bishop
	fingerprint = db_fix(fingerprint)
	finger = [i.rstrip(":") for i in chop(fingerprint, 48)]
	picture = [db_tops(i) for i in finger]
	return "".join(picture) + border

################################################################################

import hashlib

def db_scrape(fingerprint): # remove last character of each line
	room = db_multiple(fingerprint).split("\n")[:-1]
	return [item[:-1] for item in room]

def db_merge(list): # combine multiple vertical ascii frames
	super_list = [db_scrape(item) for item in list]
	output = [""] * len(super_list[0])
	for y in range(len(super_list[0])):
		for x in range(len(super_list)):
			output[y] += super_list[x][y]
		output[y] += output[y][0]
	return "\n".join(output) + "\n"

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
	return db_merge(chop(finger, constant))

################################################################################

def insert(string, char, index):
	return string[:index] + char + string[index:]

def db_supreme(passwd): # combines base69 and drunken bishop into one picture
	if isinstance(passwd, str): passwd = passwd.encode('utf-8')
	assert isinstance(passwd, bytes), "input not bytes"
	left = hashlib.md5(passwd).hexdigest() + hashlib.sha256(passwd).hexdigest()
	right = hashlib.sha384(passwd).hexdigest()
	mid = chop(hashlib.sha512(passwd).hexdigest(), 64)
	mid_left = insert(mid[0], "0" * 32, 32)
	mid_right = insert(mid[1], "0" * 32, 32)
	image = db_merge([left, mid_left, mid_right, right]).split("\n")
	for i in range(0, 9):
		image[i+11] = image[i+11][:19] + pass_check(passwd)[i]+ image[i+11][54:]
	return "\n".join(image)

################################################################################

from random import randint, shuffle

def passwd_gen(total, upcase, lowcase, numbers, others = 0, chars = ''):
	assert isinstance(total, int) and total > 0
	assert isinstance(upcase, int) and upcase >= 0
	assert isinstance(lowcase, int) and lowcase >= 0
	assert isinstance(numbers, int) and numbers >= 0
	assert isinstance(others, int) and others >= 0
	assert isinstance(chars, str)
	assert total >= ( upcase + lowcase + numbers + others )
	up_char = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	low_char = "abcdefghijklmnopqrstuvwxyz"
	num_char = "0123456789"
	chars = "+-_=.:/" if chars == '' else chars
	royale = up_char + low_char + num_char + chars
	rest = total - upcase - lowcase - numbers - others
	result = ""
	for i in range(upcase): result += up_char[randint(0, 25)]
	for i in range(lowcase): result += low_char[randint(0, 25)]
	for i in range(numbers): result += num_char[randint(0, 9)]
	for i in range(others): result += chars[randint(0, len(chars)-1)]
	for i in range(rest): result += royale[randint(0, len(royale)-1)]
	result = list(result)
	shuffle(result)
	return "".join(result)