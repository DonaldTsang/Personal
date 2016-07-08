#!/usr/bin/python
"""
Bytes (or string)
	v u2i-----+
Intger        +--encode
	v en------+
Encoded string
	v de------+
Integer       +--decode
	v i2u-----+
Bytes string
"""
import re
def chop(string, length):
	return [string[i:i+length] for i in range(0, len(string), length)]
class Codex(object):
	def __init__(self, base, exp, limit, digit):
		self.base = base
		self.exp = exp
		self.limit = limit
		self.digit = digit
	def en(integer, self): # encoding integer into text
		assert isinstance(integer, int), "Error: message not integer"
		assert 0 <= integer < (2 ** self.exp), "Error: number out of range"
		if integer == 0:
			return ''.zfill(self.limit)
		str=''
		while integer != 0:
			integer, char = divmod(integer, self.base)
			str = (self.digit[char]) + str
		return str.zfill(self.limit)[::-1]
	def de(string, self): # decoding text into integer
		assert isinstance(string, str)
		assert len(string) <= self.limit, "Error: too long"
		assert True == bool(re.fullmatch('[0-9A-Za-z_]{1,%d}' % self.limit, string))
		string = string[::-1].lstrip("0")
		integer = 0
		for char in string:
			integer *= self.base
			integer += self.digit.index(char)
		assert integer < (2 ** self.exp), "Error: number error"
		return integer
	def u2i(string, self): # encode unicode into integer
		string = string.encode('utf-8') if isinstance(string, str) else string
		assert isinstance(string, bytes), "Error: message not bytes"
		assert len(string) <= (self.exp // 8), "Error: string too long"
		result = 0
		string = string[::-1].lstrip(b'\x00')
		for char in string:
			result *= 256
			result += char
		return result
	def i2u(integer, self): # decodeing integer into unicode
		assert isinstance(integer, int), "Error: number not integer"
		assert 0 <= integer < (2 ** self.exp), "Error: number out of range"
		result = []
		while integer != 0:
			integer, r = divmod(integer, 256)
			result += [r]
		result += ( [0] * ((self.exp // 8)-len(result)) )
		return bytes(result)
	def encode(string, self): # encoding unicode into text
		return Codex.en(Codex.u2i(string, self), self)
	def decode(string, self): # decoding text into unicode
		return Codex.i2u(Codex.de(string, self), self)
	def mess_en(string, self): # encode unicode into text
		string = string.encode('utf-8') if isinstance(string, str) else string
		assert isinstance(string, bytes), "Error: message not bytes"
		string = chop(string, self.exp // 8)
		result = ''
		for steak in string:
			result += Codex.encode(steak, self)
		return result
	def mess_de(string, self): # decode text into unicode
		assert isinstance(string, str), "Error: message not string"
		string = chop(string, self.limit)
		result = b''
		for steak in string:
			result += Codex.decode(steak, self)
		return result

base63 = Codex(63, 448, 75, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_")
base62 = Codex(62, 256, 43, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
base61 = Codex(61, 160, 27, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy")
base60 = Codex(60, 112, 19, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx")