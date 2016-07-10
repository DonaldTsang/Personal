#!/usr/bin/python

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

def trim(string, length, char):
	return string.rstrip(char).ljust(length, char)

class Codex(object):

	def __init__(self, base, exp, limit, regex):
		self.base = base # Radix system inside of a  block
		self.exp = exp # Number of bits contained in a block
		self.limit = limit # Number of characters in a block
		self.regex = regex # Regex fullmatch systen of a block
		self.bound, self.byte = 2 ** self.exp, self.exp // 8

	digit = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"

	def check(self): # checks integrity of Codex
		assert isinstance(self.base, int), "Error: base not integer"
		assert 56 <= self.base < 96, "Error: base out of range"
		assert isinstance(self.exp, int), "Error: exponent not integer"
		assert self.exp % 8 == 0, "Error: exponent not multiple of 8"
		assert isinstance(self.limit, int), "Error: limit not integer"
		assert self.base ** self.limit >= self.bound, "Error: exponent too small"
		assert isinstance(regex, str), "Error: regex not string"
		assert digit[0] == "0", "Error: first digit not zero"

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
		assert True == bool(re.fullmatch(self.regex % self.limit, string))
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

	byte_list = [0, 2, 3, 5, 6, 7, 9, 10,
		11, 13, 14, 15, 17, 18, 19, 21,
		22, 23, 25, 26, 27, 29, 30, 31,
		33, 34, 35, 37, 38, 39, 41, 42,
		43, 45, 46, 47, 49, 50, 51, 53,
		54, 55, 57, 58, 59, 61, 62, 63,
		65, 66, 67, 69, 70, 71, 73, 74]

	def encode(string, self): # encoding unicode into text
		medium = Codex.en(Codex.u2i(string, self), self)
		if len(string) == self.byte: return medium
		return trim(medium, self.byte_list[len(string)], "0")

	def decode(string, self): # decoding text into unicode
		medium = Codex.i2u(Codex.de(string, self), self)
		if len(string) == self.limit: return medium
		return trim(medium, self.byte_list.index(len(string)), b"\x00")

	def mess_en(string, self): # encode unicode into text
		string = string.encode('utf-8') if isinstance(string, str) else string
		assert isinstance(string, bytes), "Error: message not bytes"
		string = chop(string, self.byte)
		return "".join([Codex.encode(steak, self) for steak in string])

	def mess_de(string, self): # decode text into unicode
		assert isinstance(string, str), "Error: message not string"
		string = chop(string, self.limit)
		return b"".join([Codex.decode(steak, self) for steak in string])

base63 = Codex(63, 448, 75, '[0-9A-Za-z_]{1,%d}')
base62 = Codex(62, 256, 43, '[0-9A-Za-z]{1,%d}')
base61 = Codex(61, 160, 27, '[0-9A-Za-y]{1,%d}')
base60 = Codex(60, 112, 19, '[0-9A-Za-x]{1,%d}')