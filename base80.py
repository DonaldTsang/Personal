#!/usr/bin/python

import re
import hashlib

"""
This is a binary-to-text encoding tool with a variety of options.

Bytes ~> Integer ~> Encoded-String ~> Integer ~> Bytes
      u2i        en                de        i2u      
       |          |                |          |       
       +----------+                +----------+       
          encode                      decode          
"""

#        |000000000111111111122222222223333333|
#        |123456789012345678901234567890123456|
digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
	'abcdefghijklmnopqrstuvwxyz.-:+=^!/*?()[]@%$#'
#   |33344444444445555555555666666666677777777778|
#   |78901234567890123456789012345678901234567890|
# This is the same character set as Z85 excluding &<>{}
# It does not includes _,;"'|\~`

def chop(string, length):
	return [string[i:i+length] for i in range(0, len(string), length)]

def check_block_mini(exp): # for 160/192/224/256-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 32 == 0, "Error: exponent not multiple of 32"
	exp //= 32
	assert 5 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 5 + 1
	base = exp + 68
	base -= 1 if base == 73 else 0
	return base, limit

def check_block_80(exp): # for 256/320/384/448/512-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 64 == 0, "Error: exponent not multiple of 64"
	exp //= 64
	assert 4 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 10 + 1
	base = exp + 73
	base -= 1 if base == 77 else 0
	base -= 1 if base == 81 else 0
	return base, limit

def check_block_76(exp): # for 320/384/448/512-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 64 == 0, "Error: exponent not multiple of 64"
	exp //= 64
	assert 5 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 10 + 2
	base = exp + 68
	base -= 1 if base == 73 else 0
	return base, limit

def check_block_72(exp): # for 384/448/512-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 64 == 0, "Error: exponent not multiple of 64"
	exp //= 64
	assert 6 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 10 + 3
	base = exp + 64
	base -= 1 if base == 70 else 0
	return base, limit

"""
def check_block_90(exp): # for 256/320/384/448/512-bits
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp % 64 == 0, "Error: exponent not multiple of 64"
	exp //= 64
	assert 4 <= exp <= 8, "Error: exponent out of range"
	limit = exp * 10 - 1
	base = 98 - exp
	base += 1 if base == 94 else 0 
	return base, limit
"""

def shifting(exp, shift = 0):
	assert isinstance(shift, int), "Error: shift not integer"
	assert 0 <= shift <= 3, "Error: shift not 0, 1, 2, or 3"
	if shift == -1 and exp = 128:
		base, limit = 69, 21
	elif shift == 0:	
		base, limit = check_block_mini(exp)
	elif shift == 1:
		base, limit = check_block_80(exp)
	elif shift == 2:
		base, limit = check_block_76(exp)
	elif shift == 3:
		base, limit = check_block_72(exp)
	return base, limit

################################################################################

def en_block(num, exp = 128, shift = -1):
	assert isinstance(num, int), "Error: message not integer"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert 0 <= num < (2 ** exp), "Error: number out of range"
	base, limit = shifting(exp, shift)
	if num == 0:
		return ''.zfill(limit)
	str=''
	while num != 0:
		num, char = divmod(num, base)
		str = (digits[char]) + str
	return str.zfill(limit)[::-1]

def de_block(string, exp = 128, shift = -1):
	assert isinstance(string, str), "Error: message not string"
	base, limit = shifting(exp, shift)
	assert len(string) <= limit, "Error: string too long"
	regex = re.fullmatch('[!#-%%(-+--:=?-Z[\]^a-z]{1,%d}' % limit, string)
	assert bool(regex) == True, "Error: unexpected character(s)"
	string = string[::-1].lstrip("0")
	num = 0
	for char in string:
		num *= base
		num += digits.index(char)
	assert num < (2 ** exp), "Error: number error"
	return num

################################################################################

def unicode2num(string, exp = 128):
	if isinstance(string, str):
		string = string.encode('utf-8')
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

def num2unicode(num, exp = 128):
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

def encode(string, exp = 128, shift = -1):
	return en_block(unicode2num(string, exp), exp, shift)

def decode(string, exp = 128, shift = -1):
	return num2unicode(de_block(string, exp, shift), exp)

################################################################################

def message_encode(string, exp = 128, shift = -1):
	if isinstance(string, str):
		string = string.encode('utf-8')
	assert isinstance(string, bytes), "Error: message not bytes"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp > 0, "Error: exponent not positive"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	base, limit = shifting(exp, shift)
	string = chop(string, exp // 8)
	result = ''
	for steak in string:
		result += encode(steak, exp, shift)
	return result

def message_decode(string, exp = 128, shift = -1):
	assert isinstance(string, str), "Error: message not string"
	assert isinstance(exp, int), "Error: exponent not integer"
	assert exp > 0, "Error: exponent not positive"
	assert exp % 8 == 0, "Error: exponent not multiple of 8"
	base, limit = shifting(exp, shift)
	string = chop(string, limit)
	result = b''
	for steak in string:
		result += decode(steak, exp, shift)
	return result

def pass_check(password):
	if isinstance(password, str):
		password = password.encode('utf-8')
	assert isinstance(password, bytes), "Error: password not bytes"
	md5_128 = hashlib.md5(password).digest()
	sha_256 = hashlib.sha256(password).digest()
	sha_384 = hashlib.sha384(password).digest()
	sha_512 = hashlib.sha512(password).digest()
	code_128 = message_encode(md5_128, 128, -1)
	code_256 = message_encode(sha_256, 128, -1)
	code_384 = message_encode(sha_384, 128, -1)
	code_512 = message_encode(sha_512, 128, -1)
	return md5_128, code_256, code_384, code_512