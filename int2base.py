from math import ceil, log

def posmod(num, den): # special modulo for int2array and int2radix
	result = num % den
	if result < 0: result += abs(den)
	return result

def int2list(num, base):
	if isinstance(num, complex) == True: 
		return [int2array(num.real, base), int2array(num.imag, base)]
	assert isinstance(num, int), "Error: input not integer"
	assert isinstance(base, int), "Error: base not integer"
	assert abs(base) >= 2, "Error: base impossible"
	if num == 0: return "0"
	if num < 0 and base > 0: return  ["-"] + int2array(-num, base)
	converted = []
	while num != 0:
		unit = posmod(num, base)
		num = (num - unit) // base
		converted += [unit]
	return converted[::-1]

def list2int(list, base):
	assert isinstance(num, int), "Error: input not integer"
	assert isinstance(base, int), "Error: base not integer"
	assert abs(base) >= 2, "Error: base impossible"
	if list[0] = "-": return -1 * list2int(list[1:], base)
	num = 0
	for item in list:
		num *= base
		num += item
	return num

def int2radix(num, base):
	if isinstance(num, complex) == True: 
		return [int2array(num.real, base), int2array(num.imag, base)]
	assert isinstance(num, int), "Error: input not integer"
	assert isinstance(base, int), "Error: base not integer"
	assert abs(base) >= 2, "Error: base impossible"
	if num == 0: return "0".zfill(ceiling)
	if num < 0 and base > 0: return "-" + int2radix(-num, base)
	ceiling = ceil(log(abs(base), 10))
	result = []
	x = int2array(num, base)
	for i in int2array(num, base):
		result += [str(i).zfill(ceiling)]
	return ":".join(result)

def int2base(num, base, alph = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
	if isinstance(num, complex) == True: 
		return [int2base(num.real, base, alph), int2base(num.imag, base, alph)]
	assert isinstance(num, int), "Error: input not integer"
	assert isinstance(base, int), "Error: base not integer"
	assert abs(base) >= 2, "Error: base impossible"
	assert len(alph) >= base, "Error: base out of range"
	assert " " not in alph, "Error: alphabet contains space"
	if num == 0: return alph[0]
	if num < 0 and base > 0:
		if "-" not in alph: return  "--" + int2base(-num, base, alph)
		elif "~" not in alph: return  "~~" + int2base(-num, base, alph)
		else: return  "negative " + int2base(-num, base, alph)
	converted = ""
	while num != 0:
		unit = posmod(num, base)
		num = (num - unit) // base
		converted += alph[unit]
	return converted[::-1]

def base2int(string, base, alph = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'):
	assert isinstance(string, str), "Error: input not string"
	assert isinstance(base, int), "Error: base not integer"
	assert abs(base) >= 2, "Error: base impossible"
	assert len(alph) >= base, "Error: base out of range"
	assert " " not in alph, "Error: alphabet contains space"
	if string[0:2] == "--" and "-" not in alph: return -1 * base2int(string[2:], base, alph)
	elif string[0:2] == "~~" and "~" not in alph: return -1 * base2int(string[2:], base, alph)
	elif string[0:9] == "negative ": return -1 * base2int(string[9:], base, alph)
	num = 0
	for char in string:
		num *= base
		num += alph.index(char)
	return num

################################################################################

def checkDubs(num, base):
	if isinstance(num, complex) == True: 
		# return a tuple
		return checkDubs(num.real, base), checkDubs(num.imag, base)
	assert isinstance(num, int), "Error: not a number"
	text = int2base(num, base)
	revtext = text[::-1]
	length = len(revtext)
	last = revtext[0]
	tuple = 0
	while(tuple <= num):
		if last != revtext[tuple]: break
		tuple += 1
	if last != '0' and tuple == length: return "Full num GET"
	elif last != '0' and tuple == length - 1: return "Half num GET"
	elif last == '0' and tuple == length - 1 and text[0] == '1': return "Full zero GET"
	elif last == '0' and tuple == length - 1 and text[0] != '1': return "Half zero GET"
	elif tuple > 1: return str(tuple) + "-tuple " + str(last) + "-s"
	else: return "Last digit is " + str(last)

def superDubs(num):
	assert isinstance(num, int), "Error: not a number"
	for i in range (8, 63):
		print("base" + str(i) + ": " + str(checkDubs(num, i)))

def checkPali(num, base):
	if isinstance(num, complex) == True: 
		# return a tuple
		return checkPali(num.real, base), checkPali(num.imag, base)
	assert isinstance(num, int), "Error: not a number"
	text = int2base(num, base)
	revtext = text[::-1]
	if text == revtext: return "full palindrome"
	length = len(revtext)
	for i in range(1, length-2): #Since doubles are not pali
		fliptext = revtext[:-i]
		revfliptext = fliptext[::-1]
		if fliptext == revfliptext:
			if len(fliptext) == length - 1: return "half palindrome"
			else: return str(length-i) + "-tuple palindrome"
	return "no palindrome"

def superPali(num):
	assert isinstance(num, int), "Error: not a number"
	for i in range (8, 63):
		print("base" + str(i) + ": " + str(checkPali(num, i)))
