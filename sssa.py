import base64, codecs
from random import SystemRandom

# https://github.com/SSSaaS/sssa-python

prime=2**256-189
hex_len = 64
b64_len = ((hex_len / 2 - 1) / 3 + 1) * 4

def random(): return SystemRandom().randrange(prime)

def split_ints(secret):
	result = []
	working, byte_object = None, None
	try: byte_object = bytes(secret, "utf8")
	except: byte_object = bytes(secret)
	text = codecs.encode(byte_object, 'hex_codec').decode('utf8') + "00"*(hex_len/2 - (len(byte_object) % (hex_len/2)))
	for i in range(0, int(len(text)/hex_len)): result.append(int(text[i*hex_len:(i+1)*hex_len], 16))
	return result

def merge_ints(secrets):
	result = ""
	for secret in secrets:
		hex_data = hex(secret)[2:]
		result += "0"*(hex_len - (len(hex_data))) + hex_data
	byte_object = None
	try:
		byte_object = bytes(result, "utf8")
		return codecs.decode(byte_object, 'hex_codec').decode('utf8').rstrip("\00\x00")
	except:
		byte_object = bytes(result)
		return codecs.decode(byte_object, 'hex_codec').rstrip("\00\x00")
	pass

def evaluate_polynomial(coefficients, value):
	result = 0
	for coefficient in reversed(coefficients):
		result *= value; result += coefficient; result %= prime
	return result

def to_base64(number):
	tmp = hex(number)[2:]
	tmp = "0"*(hex_len - len(tmp)) + tmp
	try: tmp = bytes(tmp, "utf8")
	except: tmp = bytes(tmp)
	result = str(base64.urlsafe_b64encode(b'\00'*(hex_len - len(tmp)) + codecs.decode(tmp, 'hex_codec')).decode('utf8'))
	if len(result) != b64_len/2:
		print("error: result, tmp, number")
		print(result)
		print(len(result))
		print(tmp)
		print(len(tmp))
		print(number)
		print(hex(number))
		print(hex(codecs.decode(tmp, 'hex_codec')))
	return result

def from_base64(number):
	byte_number = number
	try: byte_number = bytes(byte_number, "utf8")
	except: byte_number = bytes(byte_number)
	tmp = base64.urlsafe_b64decode(byte_number)
	try: tmp = bytes(tmp, "utf8")
	except: tmp = bytes(tmp)
	return int(codecs.encode(tmp, 'hex_codec'), 16)

def gcd(a, b):
	if b == 0: return [a, 1, 0]
	else:
		n, c = a // b, a % b
		r = gcd(b, c)
		return [r[0], r[2], r[1] - r[2]*n]

def mod_inverse(number):
		remainder = (gcd(prime, number % prime))[2]
		if number < 0: remainder *= -1
		return (prime + remainder) % prime

################################################################################

def create(minimum, shares, raw):
	if (shares < minimum): assert False, "shares should be bigger than minimum"
	secret = split_ints(raw)
	numbers = [0]
	polynomial = []
	for i in range(0, len(secret)):
		polynomial.append([secret[i]])
		for j in range(1, minimum):
			value = random()
			while value in numbers: value = random()
			numbers.append(value)
			polynomial[i].append(value)
	result = [""]*shares
	for i in range(0, shares):
		for j in range(0, len(secret)):
			value = random()
			while value in numbers: value = random()
			numbers.append(value)
			y = evaluate_polynomial(polynomial[j], value)
			result[i] += to_base64(value)
			result[i] += to_base64(y)
	return result

def combine(shares):
	secrets = []
	for index,share in enumerate(shares):
		if len(share) % b64_len != 0: return
		count = int(len(share) / b64_len)
		secrets.append([])
		for i in range(0, count):
			cshare = share[i*b64_len:(i+1)*b64_len]
			secrets[index].append([from_base64(cshare[0:b64_len/2]), from_base64(cshare[b64_len/2:b64_len])])
	secret = [0] * len(secrets[0])
	for part_index,part in enumerate(secret):
		for share_index,share in enumerate(secrets):
			origin, originy = share[part_index][0], share[part_index][1]
			numerator, denominator = 1, 1
			for product_index,product in enumerate(secrets):
				if product_index != share_index:
					current = product[part_index][0]
					numerator = (numerator * (-1*current)) % prime
					denominator = (denominator * (origin - current)) % prime
			working = ((originy * numerator * mod_inverse(denominator)) + prime)
			secret[part_index] = (secret[part_index] + working) % prime
	return merge_ints(secret)

# A message of x bytes will create a share of (x//32+1)*88 characters
