#!/usr/bin/python

import re

def chop(string, length): # chop string into blocks
	return [string[i:i+length] for i in range(0, len(string), length)]

def trim(string, length, char):
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
	digit = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
		'abcdefghijklmnopqrstuvwxyz.-:+=^!/*?()[]@%$#'
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
		assert isinstance(string, str)
		assert len(string) <= self.limit, "Error: string too long"
		assert bool(re.fullmatch(self.regex % self.limit, string))
		result, string = 0, string[::-1].lstrip("0")
		for char in string:
			result *= self.base
			result += self.digit.index(char)
		assert result < self.bound, "Error: number error"
		return result

	def u2i(string, self): # encode unicode into integer
		string = string.encode('utf-8') if isinstance(string, str) else string
		assert isinstance(string, bytes), "Error: message not bytes"
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
		string = string.encode('utf-8') if isinstance(string, str) else string
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
		80: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}',
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 14, 16, 17, 18, 19, 
			21, 22, 23, 25, 26, 27, 28, 30, 
			31, 32, 33, 35, 36, 37, 38, 40, 
			41, 42, 44, 45, 46, 47, 49, 50, 
			51, 52, 54, 55, 56, 57, 59, 60, 
			61, 63, 64, 65, 66, 68, 69, 70, 
			71, 73, 74, 75, 76, 78, 79, 80]),
		79: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}', 
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 14, 16, 17, 18, 20, 
			21, 22, 23, 25, 26, 27, 28, 30, 
			31, 32, 33, 35, 36, 37, 39, 40, 
			41, 42, 44, 45, 46, 47, 49, 50, 
			51, 53, 54, 55, 56, 58, 59, 60]),
		78: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}',
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 15, 16, 17, 18, 20, 
			21, 22, 23, 25, 26, 27, 29, 30, 
			31, 32, 34, 35, 36, 37, 39, 40, 
			41, 43, 44, 45, 46, 48, 49, 50]),
		76: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}',
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 15, 16, 17, 18, 20, 
			21, 22, 24, 25, 26, 27, 29, 30, 
			31, 33, 34, 35, 36, 38, 39, 40, 
			41, 43, 44, 45, 47, 48, 49, 50, 
			52, 53, 54, 56, 57, 58, 59, 61, 
			62, 63, 65, 66, 67, 68, 70, 71, 
			72, 73, 75, 76, 77, 79, 80, 81]),
		75: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}',
			[0, 2, 3, 4, 6, 7, 8, 9, 
			11, 12, 13, 15, 16, 17, 18, 20, 
			21, 22, 24, 25, 26, 27, 29, 30, 
			31, 33, 34, 35, 36, 38, 39, 40, 
			42, 43, 44, 45, 47, 48, 49, 51, 
			52, 53, 54, 56, 57, 58, 60, 61, 
			62, 63, 65, 66, 67, 69, 70, 71]),
		74: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}',
			[0, 2, 3, 4, 6, 7, 8, 10, 
			11, 12, 13, 15, 16, 17, 19, 20, 
			21, 22, 24, 25, 26, 28, 29, 30, 
			31, 33, 34, 35, 37, 38, 39, 40, 
			42, 43, 44, 46, 47, 48, 49, 51, 
			52, 53, 55, 56, 57, 58, 60, 61]),
		72: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}',
			[0, 2, 3, 4, 6, 7, 8, 10, 
			11, 12, 13, 15, 16, 17, 19, 20, 
			21, 23, 24, 25, 26, 28, 29, 30, 
			32, 33, 34, 36, 37, 38, 39, 41, 
			42, 43, 45, 46, 47, 48, 50, 51, 
			52, 54, 55, 56, 58, 59, 60, 61, 
			63, 64, 65, 67, 68, 69, 71, 72, 
			73, 74, 76, 77, 78, 80, 81, 82]),
		71: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}',
			[0, 2, 3, 4, 6, 7, 8, 10, 
			11, 12, 14, 15, 16, 17, 19, 20, 
			21, 23, 24, 25, 27, 28, 29, 30, 
			32, 33, 34, 36, 37, 38, 40, 41, 
			42, 43, 45, 46, 47, 49, 50, 51, 
			53, 54, 55, 56, 58, 59, 60, 62, 
			63, 64, 66, 67, 68, 69, 71, 72]),
		69: ('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}',
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

base63 = Codex(448, 63, 75, '[0-9A-Za-z_]{1,%d}', byte)
base62 = Codex(256, 62, 43, '[0-9A-Za-z]{1,%d}', byte)
base61 = Codex(160, 61, 27, '[0-9A-Za-y]{1,%d}', byte)
base60 = Codex(112, 60, 19, '[0-9A-Za-x]{1,%d}', byte)

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
def shiftz(exp): # for 256/320/384/448/512-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 64 == 0, "Error: exponent not multiple of 64"
	exp //= 64
	assert 4 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 10 - 1
	base = 98 - exp
	base += 1 if base == 94 else 0 
	return base, limit
"""
