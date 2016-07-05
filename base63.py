#!/usr/bin/python

import re

digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_'

# base=63, exp=448 (56 bytes), limit=75

def chop(string, length):
	return [string[i:i+length] for i in range(0, len(string), length)]

def divmod63(n):
	result_q, result_r = 0, n
	while result_r >= 63:
		b = result_r
		q = b >> 6
		r = b & 63
		result_q += q
		result_r = q + r
	return result_q, result_r

def en448(integer):
	assert isinstance(integer, int)
	assert isinstance(num, int), "Error: message not integer"
	assert 0 <= num < (2 ** 448), "Error: number out of range"
	if integer == 0:
		return '0'.zfill(75)
	str=''
	while integer != 0:
		integer, char = divmod(integer, 63)
		str = (digits[char]) + str
	return str.zfill(75)

def de448(string):
	assert isinstance(string, str)
	assert len(string) <= 75, "Error: too long"
	assert True == bool(re.fullmatch('[0-9A-Za-z_]{1,75}', string))
	string = string.lstrip("0")
	num = 0
	for char in string:
		num *= 63
		num += digits.index(char)
	assert num < (2 ** 448), "Error: number error"
	return num

################################################################################

def unicode2num(string):
	assert isinstance(string, bytes), "Error: message not bytes"
	assert len(string) <= 56, "Error: string too long"
	result = 0
	string = string[::-1].lstrip(b'\x00')
	for char in string:
		result *= 256
		result += char
	return result

def num2unicode(num):
	assert isinstance(num, int), "Error: number not integer"
	assert 0 <= num < (2 ** 448), "Error: number out of range"
	result = []
	while num != 0:
		num, r = divmod(num, 256)
		result += [r]
	result += ( [0] * (56-len(result)) )
	return bytes(result)

################################################################################

def encode448(string):
	return en448(unicode2num(string))

def decode448(string):
	return num2unicode(de448(string))

################################################################################

def message_encode448(string):
	assert isinstance(string, bytes), "Error: message not bytes"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	string = chop(string, 56)
	result = ''
	for steak in string:
		result += encode448(steak)
	return result

def message_decode(string):
	assert isinstance(string, str), "Error: message not bytes"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	string = chop(string, 75)
	result = b''
	for steak in string:
		result += decode448(steak)
	return result