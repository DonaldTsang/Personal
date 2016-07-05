#!/usr/bin/python

import re

digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

"""
Bytes (or string)
	v unicode2num --+
Intger              +--encode
	v en_block -----+
Encoded string
	v de_block -----+
Integer             +--decode
	v num2unicode --+
Bytes string

"""

def chop(string, length):
	return [string[i:i+length] for i in range(0, len(string), length)]

def check_block(exp):
	assert isinstance(exp, int), "Error: exponent not integer"
	if exp % 16 != 0:
		return False # exp not 16
	exp //= 16
	if exp % 16 == 0:
		return 62, 43
	elif exp % 10 == 0:
		return 61, 27
	elif exp % 7 == 0:
		return 60, 19
	else:
		return False

def en_block(num, exp):
	assert isinstance(num, int), "Error: message not integer"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert 0 <= num < (2 ** exp), "Error: number out of range"
	assert check_block(exp) != False, "Error: bad exponent"
	base, limit = check_block(exp)
	if num == 0:
		return ''.zfill(limit)
	str=''
	while num != 0:
		num, char = divmod(num, base)
		str = (digits[char]) + str
	return str.zfill(limit)[::-1]

def de_block(string, exp):
	assert isinstance(string, str)
	assert check_block(exp) != False, "Error: bad exponent"
	base, limit = check_block(exp)
	assert len(string) <= limit, "Error: too long"
	assert True == bool(re.fullmatch('[0-9A-Za-z]{1,%d}' % limit, string))
	string = string[::-1].lstrip("0")
	num = 0
	for char in string:
		num *= base
		num += digits.index(char)
	assert num < (2 ** exp), "Error: number error"
	return num

################################################################################

def unicode2num(string, exp):
	assert isinstance(string, bytes), "Error: message not bytes"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp > 0, "Error: exponent not positive"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	assert len(string) <= (exp // 8), "Error: string too long"
	result = 0
	string = string[::-1].lstrip(b'\x00')
	for char in string:
		result *= 256
		result += char
	return result

def num2unicode(num, exp):
	assert isinstance(num, int), "Error: number not integer"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp > 0, "Error: exponent not positive"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	assert 0 <= num < (2 ** exp), "Error: number out of range"
	result = []
	while num != 0:
		num, r = divmod(num, 256)
		result += [r]
	result += ( [0] * (exp//8-len(result)) )
	return bytes(result)

################################################################################

def encode(string, exp):
	return en_block(unicode2num(string, exp), exp)

def decode(string, exp):
	return num2unicode(de_block(string, exp), exp)

################################################################################

def message_encode(string, exp):
	assert isinstance(string, bytes), "Error: message not bytes"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp > 0, "Error: exponent not positive"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	base, limit = check_block(exp)
	string = chop(string, exp // 8)
	result = ''
	for steak in string:
		result += encode(steak, exp)
	return result

def message_decode(string, exp, shift):
	assert isinstance(string, str), "Error: message not string"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp > 0, "Error: exponent not positive"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	base, limit = check_block(exp)
	string = chop(string, limit)
	result = b''
	for steak in string:
		result += decode(steak, exp)
	return result

################################################################################

def divmod62(x):
	a, q, r = 0, x, 0
	while q >= 62:
		r = q & 63 # r = q % 64
		q >>= 6 # q = q
		a += q # a = a + q
		q <<= 1 # q = q * 2
		q += r # q = q + r
	return a, q # div and mod
