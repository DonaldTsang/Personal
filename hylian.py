import re

hylian = ' ABCDEFGHIJKLMNOPRSTUVWXYZ.'

def format_message(message, replace=" "):
	message = message.upper()
	message = re.sub("0", "ZERO" + replace, message)
	message = re.sub("1", "ONE" + replace, message)
	message = re.sub("2", "TWO" + replace, message)
	message = re.sub("3", "THREE" + replace, message)
	message = re.sub("4", "FOUR" + replace, message)
	message = re.sub("5", "FIVE" + replace, message)
	message = re.sub("6", "SIX" + replace, message)
	message = re.sub("7", "SEVEN" + replace, message)
	message = re.sub("8", "EIGHT" + replace, message)
	message = re.sub("9", "NINE" + replace, message)
	return re.sub("[^A-PR-Z. ]", "", message)

def en(integer, block_len): # encode integer into text
	assert isinstance(integer, int), "Error: message not integer"
	assert 0 <= integer < 27 ** block_len, "Error: number out of range"
	if integer == 0: return " " * self.limit
	result=""
	while integer != 0:
		integer, char = divmod(integer, 27); result += hylian[char]
	return result.ljust(block_len, " ")

def de(string, block_len): # decode text into integer
	assert isinstance(string, str), "Error: message not string"
	assert len(string) <= block_len, "Error: string too long"
	assert bool(re.fullmatch("[A-PR-Z. ]{1,%d}" % block_len, string))
	result, string = 0, string[::-1].lstrip(" ")
	for char in string:
		result *= 27; result += hylian.index(char)
	assert result < 27 ** block_len, "Error: number error"
	return result

def egcd(a, b): # extended greatest common divisor
	if a == 0: return (b, 0, 1)
	else:
		g, y, x = egcd(b % a, a)
		return (g, x - (b // a) * y, y)

def modinv(a, m): # multiplicative modular inverse
	g, x, y = egcd(a, m)
	if g != 1: raise Exception('modular inverse does not exist')
	else: return x % m

def affine_check(block_len, add, mult):
	assert isinstance(block_len, int) and block_len > 0
	max = 27 ** block_len
	assert isinstance(add, int) and 0 <= add < max
	assert isinstance(mult, int) and 0 < mult < max and egcd(mult, 27)[0] == 1 

def affine_en(integer, block_len, add, mult): # encrypts integer using affine
	assert isinstance(integer, int)
	affine_check(block_len, add, mult)
	return (integer * mult + add) % (27 ** block_len)

def affine_de(integer, block_len, add, mult): # decrypts integer using affine
	assert isinstance(integer, int)
	affine_check(block_len, add, mult)
	result = (integer - add) % (27 ** block_len)
	return result * modinv(mult, 27 ** block_len) % (27 ** block_len)

################################################################################

# string = sentence in hylian including space and periods
# block_len = numbe rof characters in a block of code
# add, mult = additive and multiplicative key of cipher

def check(block_len, add, mult):
	assert isinstance(block_len, int) and block_len > 0
	max = 27 ** block_len
	assert isinstance(add, int) and 0 <= add < max
	assert isinstance(mult, int) and 1 <= mult < max and egcd(mult, 27)[0] == 1 

def encrypt(string, block_len, add, mult): # encrypts hylian
	assert isinstance(string, str)
	check(block_len, add, mult)
	chop = [string[i:i+block_len] for i in range(0, len(string), block_len)]
	result = ''
	for item in chop:
		part = en(affine_en(de(item, block_len),block_len, add, mult), block_len)
		result += part
	return result

def decrypt(string, block_len, add, mult): # decrypts hylian
	assert isinstance(string, str)
	check(block_len, add, mult) 
	chop = [string[i:i+block_len] for i in range(0, len(string), block_len)]
	result = ''
	for item in chop:
		part = en(affine_de(de(item, block_len),block_len, add, mult), block_len)
		result += part
	return result

################################################################################

from random import randint

def hylian_gen(block_len): # create key for single hylian cipher
	add = randint(0, 27 ** block_len - 1)
	mult_1 = randint(0, 27 ** (block_len - 1) - 1) * 27
	mult_2 = [1,2,4,5,7,8,10,11,13,14,16,17,19,20,22,23,25,26][randint(0, 17)]
	return [block_len, add, mult_1 + mult_2]

def triple_hylian(): # creates large keys for triple hylain cipher
	hyrule = [2, 2, 2]
	while egcd(egcd(hyrule[0], hyrule[1])[0], hyrule[2])[0] != 1:
		block_pool, hyrule = list(range(9, 28)), []
		for i in range(0, 3):
			hyrule.append(block_pool.pop(randint(0,len(block_pool)-1)))
	for i in range(0, 3): hyrule[i] = hylian_gen(hyrule[i])
	return hyrule

def triple_hylian_simple(): # creates small keys for triple hylain cipher
	hyrule = [2, 2, 2]
	while egcd(egcd(hyrule[0], hyrule[1])[0], hyrule[2])[0] != 1:
		block_pool, hyrule = list(range(3, 9)), []
		for i in range(0, 3):
			hyrule.append(block_pool.pop(randint(0,len(block_pool)-1)))
	for i in range(0, 3): hyrule[i] = hylian_gen(hyrule[i])
	return hyrule

################################################################################

def hylian_layout_en(message=''):
	if message == '': print('type message with no newline'); message = input()
	message_chop = [message[i:i+81] for i in range(0, len(message), 81)] + [""]
	message_clean = "\n".join(message_chop)
	return "------BEGIN GGR MESSAGE------\n" + \
		"Version: DDMoe v.1.4.88 (Heil.OS)\n" + \
		"\n" + \
		message_clean + \
		"------END GGR MESSGAE------"

def multiline():
	print("Enter as many lines of text as needed.")
	print("When done, enter '>' on a line by itself.")
	buffer = []
	while True:
	    line = input()
	    if line == ">": break
	    buffer.append(line)
	return "\n".join(buffer)

def hylian_layout_de(message=''):
	if message == '': message = multiline()
	message_pure = message.rstrip("\n").split("\n")
	return "".join(message_pure).rstrip("------END GGR MESSGAE------") \
		.lstrip("------BEGIN GGR MESSAGE------Version: DDMoe v.1.4.88 (Heil.OS)")
