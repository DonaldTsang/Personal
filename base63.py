#!#!/usr/bin/python
"""
This is a binary-to-text encoding tool with a variety of options.

Bytes ~> Integer ~> Encoded-String ~> Integer ~> Bytes
      u2i        en                de        i2u      
       |          |                |          |       
       +----------+                +----------+       
          encode                      decode          
"""
import re

def chop(string, length): # chop string into blocks
	return [string[i:i+length] for i in range(0, len(string), length)]

class Codex(object):

	def __init__(self, base, exp, limit, regex):
		self.base = base
		self.exp = exp
		self.limit = limit
		self.regex = regex

	def check(self):
		assert isinstance(base, int), "Error: base not integer"
		assert 56 <= base < 96, "Error: base out of range"
		assert isinstance(exp, int), "Error: exponent not integer"
		assert exp % 8 == 0, "Error: exponent not multiple of 8"
		assert isinstance(limit, int), "Error: limit not integer"
		assert isinstance(regex, str), "Error: regex not string"
		assert digit[0] == "0", "Error: first digit not zero"
		return True
	
	digit = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"

	def en(integer, self): # encoding integer into text
		assert isinstance(integer, int), "Error: message not integer"
		assert 0 <= integer < (2 ** self.exp), "Error: number out of range"
		if integer == 0:
			return ''.zfill(self.limit)
		string=''
		while integer != 0:
			integer, char = divmod(integer, self.base)
			string += self.digit[char]
		return string.ljust(self.limit, "0")

	def de(string, self): # decoding text into integer
		assert isinstance(string, str)
		assert len(string) <= self.limit, "Error: string too long"
		assert True == bool(re.fullmatch(self.regex % self.limit, string))
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
		result += ([0] * ((self.exp // 8)-len(result)))
		return bytes(result)

	byte_list = [0, 2, 3, 5, 6, 7, 9, 10,
		11, 13, 14, 15, 17, 18, 19, 21,
		22, 23, 25, 26, 27, 29, 30, 31,
		33, 34, 35, 37, 38, 39, 41, 42,
		43, 45, 46, 47, 49, 50, 51, 53,
		54, 55, 57, 58, 59, 61, 62, 63,
		65, 66, 67, 69, 70, 71, 73, 74]

	def encode(string, self): # encoding unicode into text
		medium = Codex.en(Codex.u2i(string, self), self)
		if len(string) == self.exp // 8:
			return medium
		return medium.rstrip("0").ljust(self.byte_list[len(string)], "0")

	def decode(string, self): # decoding text into unicode
		medium = Codex.i2u(Codex.de(string, self), self)
		if len(string) == self.limit:
			return medium
		return medium.rstrip(b"\x00").ljust(self.byte_list.index(len(string)), b"\x00")

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

base63 = Codex(63, 448, 75, '[0-9A-Za-z_]{1,%d}')
base62 = Codex(62, 256, 43, '[0-9A-Za-z]{1,%d}')
base61 = Codex(61, 160, 27, '[0-9A-Za-y]{1,%d}')
base60 = Codex(60, 112, 19, '[0-9A-Za-x]{1,%d}')