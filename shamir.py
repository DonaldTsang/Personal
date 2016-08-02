from math import ceil, log

def calculate_mersenne_primes():
	# Returns all the mersenne primes with less than 500 digits.
	mersenne_prime_exponents = [
		2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279]
	primes = []
	for exp in mersenne_prime_exponents:
		prime = 1
		for i in range(exp): prime *= 2
		prime -= 1; primes.append(prime)
	return primes

SMALLEST_0065BIT_PRIME = (2**64 + 13)
SMALLEST_0081BIT_PRIME = (2**80 + 13)
SMALLEST_0097BIT_PRIME = (2**96 + 61)
SMALLEST_0112BIT_PRIME = (2**112 + 25)
SMALLEST_0129BIT_PRIME = (2**128 + 51)
SMALLEST_0161BIT_PRIME = (2**160 + 7)
SMALLEST_0193BIT_PRIME = (2**192 + 133)
SMALLEST_0225BIT_PRIME = (2**224 + 735)
SMALLEST_0257BIT_PRIME = (2**256 + 297)
SMALLEST_0321BIT_PRIME = (2**320 + 27)
SMALLEST_0385BIT_PRIME = (2**384 + 231)
SMALLEST_0449BIT_PRIME = (2**448 + 211)
SMALLEST_0513BIT_PRIME = (2**512 + 75)
SMALLEST_0641BIT_PRIME = (2**640 + 115)
SMALLEST_0769BIT_PRIME = (2**768 + 183)
SMALLEST_0897BIT_PRIME = (2**896 + 993)
SMALLEST_1025BIT_PRIME = (2**1024 + 643)
SMALLEST_PRIMES = [
	SMALLEST_0257BIT_PRIME, SMALLEST_0321BIT_PRIME, SMALLEST_0385BIT_PRIME]
STANDARD_PRIMES = calculate_mersenne_primes() + SMALLEST_PRIMES
STANDARD_PRIMES.sort()

def get_large_enough_prime(batch):
	# Returns a prime number that is greater all the numbers in the batch.
	# build a list of primes
	primes = STANDARD_PRIMES
	# find a prime that is greater than all the numbers in the batch
	for prime in primes:
		numbers_greater_than_prime = [i for i in batch if i > prime]
		if len(numbers_greater_than_prime) == 0: return prime
	return None

################################################################################

from random import randint

def egcd(a, b):
	if a == 0: return (b, 0, 1)
	else:
		g, y, x = egcd(b % a, a)
		return (g, x - (b // a) * y, y)

def xgcd(b, n):
	x0, x1, y0, y1 = 1, 0, 0, 1
	while n != 0:
		q, b, n = b // n, n, b % n
		x0, x1 = x1, x0 - q * x1
		y0, y1 = y1, y0 - q * y1
	return  b, x0, y0

def mod_inverse(k, prime):
	k %= prime
	if k < 0: r = egcd(prime, -k)[2]
	else: r = egcd(prime, k)[2]
	return (prime + r) % prime

def random_polynomial(degree, intercept, upper_bound):
	# Generates a random polynomial with positive coefficients.
	if degree < 0: raise ValueError('Degree must be non-negative.')
	coefficients = [intercept]
	for i in range(degree):
		random_coeff = randint(0, upper_bound-1)
		coefficients.append(random_coeff)
	return coefficients

def get_polynomial_points(coefficients, num_points, prime):
	# Calculates the first n polynomial points.
	# [ (1, f(1)), (2, f(2)), ... (n, f(n)) ]
	points = []
	for x in range(1, num_points+1):
		# start with x=1 and calculate the value of y
		y = coefficients[0]
		# calculate each term and add it to y, using modular math
		for i in range(1, len(coefficients)):
			exponentiation = (x**i) % prime
			term = (coefficients[i] * exponentiation) % prime
			y += term; y %= prime
		# add the point to the list of points
		points.append((x, y))
	return points

def modular_lagrange_interpolation(x, points, prime):
	# break the points up into lists of x and y values
	x_values, y_values = zip(*points)
	# initialize f(x) and begin the calculation: f(x) = SUM( y_i * l_i(x) )
	f_x = 0
	for i in range(len(points)):
		# evaluate the lagrange basis polynomial l_i(x)
		numerator, denominator = 1, 1
		for j in range(len(points)):
			# don't compute a polynomial fraction if i equals j
			if i == j: continue
			# compute a fraction & update the existing numerator + denominator
			numerator = (numerator * (x - x_values[j])) % prime
			denominator = (denominator * (x_values[i] - x_values[j])) % prime
		# get the polynomial from the numerator + denominator mod inverse
		lagrange_polynomial = numerator * mod_inverse(denominator, prime)
		# multiply the current y & the evaluated polynomial & add it to f(x)
		f_x = (prime + f_x + (y_values[i] * lagrange_polynomial)) % prime
	return f_x

################################################################################

def int_to_charset(val, charset):
	# Turn a non-negative integer into a string.
	if not val >= 0:
		raise ValueError('"val" must be a non-negative integer.')
	if val == 0: return charset[0]
	output = ""
	while val > 0:
		val, digit = divmod(val, len(charset))
		output += charset[digit]
	# reverse the characters in the output and return
	return output[::-1]

def charset_to_int(s, charset):
	# Turn a string into a non-negative integer.
	output = 0
	for char in s: output *= len(charset); output += charset.index(char)
	return output

################################################################################

import string

def secret_int_to_points(secret_int, point_threshold, num_points, prime=None):
	# Split a secret integer into shares (pair of integers or x,y coords).
	# Sample points of a random polynomial with y intercept equal to secret int.
	if point_threshold < 2:
		raise ValueError("Threshold must be >= 2.")
	if point_threshold > num_points:
		raise ValueError("Threshold must be < the total number of points.")
	if not prime:
		prime = get_large_enough_prime([secret_int, num_points])
		if not prime:
			raise ValueError("Secret is too long for share calculation!")
	coefficients = random_polynomial(point_threshold-1, secret_int, prime)
	points = get_polynomial_points(coefficients, num_points, prime)
	return points

def points_to_secret_int(points, prime=None):
	# Join int points into a secret int.
	# Get the intercept of a random polynomial defined by the given points.

	if not isinstance(points, list):
		raise ValueError("Points must be in list form.")
	for point in points:
		if not isinstance(point, tuple) and len(point) == 2:
			raise ValueError("Each point must be a tuple of two values.")
		if not (isinstance(point[0], int) and isinstance(point[1], int)):
			raise ValueError("Each value in the point must be an int.")
	x_values, y_values = zip(*points)
	if not prime:
		prime = get_large_enough_prime(y_values)
		if not prime:
			raise ValueError("Error! Point is too large for share calculation!")
	free_coefficient = modular_lagrange_interpolation(0, points, prime)
	secret_int = free_coefficient  # the secret int is the free coefficient
	return secret_int

def point_to_share_string(point, n, char_count, charset, num_leading_zeros):
	# Convert a point (a tuple of two integers) into a share string - that is,
	# a representation of the point that uses the charset provided.
	# point should be in the format (1, 4938573982723...)
	if '~' in charset:
		raise ValueError(
			'The character "~" cannot be in the supplied charset.')
	if not (isinstance(point, tuple) and len(point) == 2 and
			isinstance(point[0], int) and isinstance(point[1], int)):
		raise ValueError(
			'Point format is invalid. Must be a pair of integers.')
	x, y = point
	x_string, y_string = int_to_charset(x, charset), int_to_charset(y, charset)
	share_string = x_string.rjust(n, charset[0]) + '~' + y_string.rjust(char_count, charset[0])
	if num_leading_zeros != 0:
		share_string += '~' + int_to_charset(num_leading_zeros, charset)
	return share_string

def share_string_to_point(share_string, charset):
	# Convert a share string to a point (a tuple of integers).
	# share should be in the format "01-d051080de7..."
	if '-' in charset:
		raise ValueError(
			'The character "-" cannot be in the charset.')
	if not isinstance(share_string, str):
		raise ValueError('Share format is invalid.')
	num_leading_zeros = None
	if share_string.count('~') == 1:
		x_string, y_string = share_string.split('~')
	elif share_string.count('~') == 2:
		x_string, y_string, num_leading_zeros = share_string.split('~')
	else:
		raise ValueError('Share format is invalid.')
	if (set(x_string) - set(charset)) or (set(y_string) - set(charset)):
		raise ValueError("Share has characters that aren't in the charset.")
	x, y = charset_to_int(x_string, charset), charset_to_int(y_string, charset)
	if num_leading_zeros:
		num_leading_zeros = charset_to_int(num_leading_zeros, charset)
	return (x, y), num_leading_zeros

class SS():
	""" Creates a secret sharer, which can convert from a secret string to a
		list of shares and vice versa. The splitter is initialized with the
		character set of the secrets and the character set of the shares that
		it expects to be dealing with.
	"""
	def __init__(self, secret_charset, share_charset):
		self.secret_charset = secret_charset
		self.share_charset = share_charset

	def split(self, secret_string, share_threshold, num_shares):
		num_leading_zeros = 0
		for secret_char in secret_string:
			if secret_char == self.secret_charset[0]: num_leading_zeros += 1
			else: break
		secret_int = charset_to_int(secret_string, self.secret_charset)
		points = secret_int_to_points(secret_int, share_threshold, num_shares)
		maxim = 0
		for point in points:
			if point[1] > maxim: maxim = point[1]
		char_count = ceil(log(maxim, len(self.share_charset)))
		n = ceil(log(num_shares, len(self.share_charset)))
		shares = []
		for point in points:
			share_string = point_to_share_string(
				point, n, char_count, self.share_charset, num_leading_zeros)
			shares.append(share_string)
		return shares

	def recover(self, shares):
		num_leading_zeros = None
		points = []
		for share in shares:
			point, num_leading_zeros = share_string_to_point(
				share, self.share_charset)
			points.append(point)
		secret_int = points_to_secret_int(points)
		secret_string = int_to_charset(secret_int, self.secret_charset)
		if num_leading_zeros:
			leading_zeros = self.secret_charset[0] * num_leading_zeros
			secret_string = leading_zeros + secret_string
		return secret_string

b16 = string.hexdigits[0:16]
b32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + \
	"0123456789+/"
url = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + \
	"0123456789-_"
unix = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" + \
	"abcdefghijklmnopqrstuvwxyz"
ascii = string.printable # cannot be used for share_charset

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Shamir Secret Sharer')
	sub_split = parser.add_subparsers()
	sub_split.add_parser("split", action="store_true", default=False
		help="Split password into multiple sub-passwords")
	sub_split.add_argument("password", type=str)
	sub_split.add_argument("share_threshold", type=int)
	sub_split.add_argument("num_shares", type=int)
	sub_recover = parser.add_subparsers()
	sub_recover.add_parser("recover", action="store_true", default=False
		help="Recover password from multiplr sub-passwords")
	sub_recover.add_argument("share_list", type=list)
	parser.add_argument("secret_charset", choices=["b16", "b32", "b64", "url", "unix", "ascii"],
		default="b16", help="Encoding system of password")
	parser.add_argument("share_charset", choices=["b16", "b32", "b64", "url", "unix"],
		default="b16", help="Encoding system of sub-passwords")
	args = parser.parse_args()
	SS_new = SS(secret_charset, share_charset)
	if args.split == True: print(SS_new.split(password, share_threshold, num_shares))
	elif args.recover == True: print(SS_new.recover(share_list))
