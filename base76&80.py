#!/usr/bin/python

import hashlib

digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
	'abcdefghijklmnopqrstuvwxyz.-:+=^!/*?()[]@%$#'

def chop(string, length):
	return [string[i:i+length] for i in range(0, len(string), length)]

def check_block_76(exp): # for 160/192/224/256-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 32 == 0, "Error: exponent not multiple of 32"
	exp //= 32
	assert 4 < exp <= 8, "Error: exponent out of range"
	limit = exp * 5 + 1
	base = exp + 68
	if base == 73:
		base = 72
	return base, limit

def check_block_80(exp): # for 256/320/384/448/512-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 64 == 0, "Error: exponent not multiple of 64"
	exp //= 64
	assert 4 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 10 + 1
	base = exp + 73
	if base == 77:
		base = 76
	elif base == 81:
		base = 80
	return base, limit

def check_block_72(exp): # for 448/512-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 64 == 0, "Error: exponent not multiple of 64"
	exp //= 64
	assert 7 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 10 + 3
	base = exp + 64
	return base, limit

"""
def check_block_90(exp): # for 256/320/384/448/512-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 64 == 0, "Error: exponent not multiple of 64"
	exp //= 64
	assert 4 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 10 - 1
	base = 98 - exp
	if base == 94:
		base = 95
	return base, limit
"""

def shifting(exp, shift):
	assert shift == 0 or shift == 1, "Error: shift not 0 or 1"
	if shift == 0:	
		base, limit = check_block_76(exp)
	elif shift == 1:
		base, limit = check_block_80(exp)
	else:
		base, limit = check_block_72(exp)
	return base, limit

################################################################################

def en_block(num, exp, shift):
	assert isinstance(num, int), "Error: message not integer"
	assert 0 <= num < (2 ** exp), "Error: number out of range"
	base, limit = shifting(exp, shift)
	if num == 0:
		return ''.zfill(limit)
	str=''
	while num != 0:
		num, char = divmod(num, base)
		str = (digits[char]) + str
	return str.zfill(limit)[::-1]

def de_block(string, exp, shift):
	assert isinstance(string, str), "Error: message not string"
	base, limit = shifting(exp, shift)
	assert len(string) <= limit, "Error: too long"
	# assert True == bool(re.fullmatch('[0-9A-Za-z]{1,%d}' % limit, string))
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

def encode(string, exp, shift):
	return en_block(unicode2num(string, exp), exp, shift)

def decode(string, exp, shift):
	return num2unicode(de_block(string, exp, shift), exp)

################################################################################

def message_encode(string, exp, shift):
	assert isinstance(string, bytes), "Error: message not bytes"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	base, limit = shifting(exp, shift)
	string = chop(string, exp // 8)
	result = ''
	for steak in string:
		result += encode(steak, exp, shift)
	return result

def message_decode(string, exp, shift):
	assert isinstance(string, str), "Error: message not bytes"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	base, limit = shifting(exp, shift)
	string = chop(string, limit)
	result = b''
	for steak in string:
		result += decode(steak, exp, shift)
	return result

def pass_check(password):
	password = password.encode('utf-8')
	sha_256 = hashlib.sha256(password).digest()
	sha_384 = hashlib.sha384(password).digest()
	sha_512 = hashlib.sha512(password).digest()
	code_256 = message_encode(sha_256, 256, 1)
	code_384 = message_encode(sha_384, 384, 1)
	code_512 = message_encode(sha_512, 512, 1)
	return code_256, code_384, code_512
