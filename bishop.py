#!/usr/bin/python

import hashlib
import itertools
from collections import Counter


"""
The bishop wakes up in the center of a room. He is drunk and stumbles around,
putting down coins at each position he passes. The bishop only walks diagonally
much like bishops normally found on chess boards. The fingerprint determines
his steps.

The room is 17 positions wide and 9 positions long. The bishop starts in the
center of the room.
"""


# the bishop starts in the center of the room
STARTING_POSITION = (8, 4)
ROOM_DIMENSIONS = (17, 9)

# encode start and end positions
COIN_VALUE_STARTING_POSITION = 15
COIN_VALUE_ENDING_POSITION = 16

BORDER = '+' + '-' * ROOM_DIMENSIONS[0] + '+\n'


def hex_byte_to_binary(hex_byte):
    """
    Convert a hex byte into a string representation of its bits,
    e.g. 'd4' => '11010100'
    """
    assert len(hex_byte) == 2
    dec = int(hex_byte, 16)
    return bin(dec)[2:].zfill(8)


def bit_pairs(binary):
    """
    Convert a word into bit pairs little-endian style.
    '10100011' => ['11', '00', '10', '10']
    """
    def take(n, iterable):
        "Return first n items of the iterable as a list"
        return list(itertools.islice(iterable, n))
    def all_pairs(iterable):
        while True:
            pair = take(2, iterable)
            if not pair:
                break
            yield ''.join(pair)
    pairs = list(all_pairs(iter(binary)))
    return list(reversed(pairs))


class Direction(object):
    """Encode a sense of direction."""
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

NW = Direction(dx=-1, dy=-1)
NE = Direction(dx=1, dy=-1)
SW = Direction(dx=-1, dy=1)
SE = Direction(dx=1, dy=1)


def directions_from_fingerprint(fingerprint):
    """
    Convert the fingerprint (16 hex-encoded bytes separated by colons)
    to steps (one of four directions: NW, NE, SW, SE).
    """
    direction_lookup = {
        '00': NW,
        '01': NE,
        '10': SW,
        '11': SE,
    }
    for hex_byte in fingerprint.split(':'):
        binary = hex_byte_to_binary(hex_byte)
        # read each bit-pair in each word right-to-left (little endian)
        for bit_pair in bit_pairs(binary):
            direction = direction_lookup[bit_pair]
            yield direction


def move(position, direction):
    """
    Returns new position given current position and direction to move in.
    """
    x, y = position
    MAX_X = ROOM_DIMENSIONS[0] - 1
    MAX_Y = ROOM_DIMENSIONS[1] - 1
    assert 0 <= x <= MAX_X
    assert 0 <= y <= MAX_Y
    new_x, new_y = x + direction.dx, y + direction.dy
    # the drunk bishop is hindered by the wall.
    new_x = 0 if new_x <= 0 else min(new_x, MAX_X)
    new_y = 0 if new_y <= 0 else min(new_y, MAX_Y)
    return new_x, new_y


def stumble_around(fingerprint):
    room = Counter()
    position = STARTING_POSITION
    for direction in directions_from_fingerprint(fingerprint):
        position = move(position, direction)
        room[position] += 1  # drop coin
    # mark start and end positions
    room[STARTING_POSITION] = COIN_VALUE_STARTING_POSITION
    room[position] = COIN_VALUE_ENDING_POSITION
    return room


def coin(value):
    """
    Display the ascii representation of a coin.
    """
    return {
        0: ' ',
        1: '.',
        2: 'o',
        3: '+',
        4: '=',
        5: '*',
        6: 'B',
        7: 'O',
        8: 'X',
        9: '@',
        10: '%',
        11: '&',
        12: '#',
        13: '/',
        14: '^',
        COIN_VALUE_STARTING_POSITION: 'S',
        COIN_VALUE_ENDING_POSITION: 'E',
    }.get(value, '!')


def display_room(room):
    X, Y = ROOM_DIMENSIONS
    def room_as_strings():
        yield BORDER
        for y in range(Y):
            yield '|'
            for x in range(X):
                yield coin(room[(x,y)])
            yield '|\n'
        yield BORDER
    return ''.join(room_as_strings())


################################################################################


def drunken_bishop_colon(fingerprint):
	"""
	Inserts colon to hex strings.
	"""
	assert len(fingerprint) % 2 == 0
	result = ""
	for i in range(len(fingerprint)//2):
		result =  result + fingerprint[2*i:2*i+2] + ':'
	return result[:-1]


def drunken_bishop_check(fingerprint):
	if ":" not in fingerprint:
		return False # Hex pairs without colon
	else:
		return True # Hex pairs with colon


def drunken_bishop(fingerprint):
	"""
	Creates a piece of art base on 32 hex
	"""
	if drunken_bishop_check(fingerprint) == False:
		fingerprint = drunken_bishop_colon(fingerprint)
	room = stumble_around(fingerprint)
	return display_room(room)


def drunken_bishop_tops(fingerprint):
	"""
	Like drunken_bishop but without the bottom frame
	"""
	if drunken_bishop_check(fingerprint) == False:
		fingerprint = drunken_bishop_colon(fingerprint)
	room = stumble_around(fingerprint)
	return display_room(room)[:-(ROOM_DIMENSIONS[0]+3)]


def drunken_bishop_multiple(fingerprint):
	"""
	Vertically stacked drunken_bishop
	"""
	if drunken_bishop_check(fingerprint) == False:
		fingerprint = drunken_bishop_colon(fingerprint)
	finger = [fingerprint[i:i+48].rstrip(':') for i in range(0, len(fingerprint), 48)]
	picture = [drunken_bishop_tops(i) for i in finger]
	return ''.join(picture) + BORDER


################################################################################


def drunken_bishop_scrape(fingerprint):
	room = drunken_bishop_multiple(fingerprint)
	scan = room.split('\n')[:-1]
	return [item[:-1] for item in scan]


def drunken_bishop_merge(list):
	super_list = []
	for item in list:
		super_list.append(drunken_bishop_scrape(item))
	output = [''] * len(super_list[0])
	for y in range(len(super_list[0])):
		for x in range(len(super_list)):
			output[y] += super_list[x][y]
		output[y] += output[y][0]
	return '\n'.join(output) + '\n'


def chop(string, length):
	return [string[i:i+length] for i in range(0, len(string), length)]


def drunken_bishop_1x1(password):
	"""
	A 1x1 drunken_bishop rectangle based on MD-5
	"""
	password = password.encode('utf-8')
	md5 = hashlib.md5(password).hexdigest()
	md5_finger = chop(md5, 32)
	return drunken_bishop_merge(md5_finger)


def drunken_bishop_1x2(password):
	"""
	A 1x2 drunken_bishop rectangle based on SHA-256
	"""
	password = password.encode('utf-8')
	sha_256 = hashlib.sha256(password).hexdigest()
	sha_finger = chop(sha_256, 32)
	return drunken_bishop_merge(sha_finger)


def drunken_bishop_2x2(password):
	"""
	A 2x2 drunken_bishop rectangle based on SHA-512
	"""
	password = password.encode('utf-8')
	sha_512 = hashlib.sha512(password).hexdigest()
	sha_finger = chop(sha_512, 64)
	return drunken_bishop_merge(sha_finger)


def drunken_bishop_2x3(password):
	"""
	A 2x3 drunken_bishop rectangle based on SHA-256/512
	"""
	password = password.encode('utf-8')
	sha_256 = hashlib.sha256(password).hexdigest()
	sha_512 = hashlib.sha512(password).hexdigest()
	sha_ultra = sha_256 + sha_512
	sha_finger = chop(sha_ultra, 64)
	return drunken_bishop_merge(sha_finger)


def drunken_bishop_3x3(password):
	"""
	A 3x3 drunken_bishop rectangle based on SHA-256/384/512
	"""
	password = password.encode('utf-8')
	sha_256 = hashlib.sha256(password).hexdigest()
	sha_384 = hashlib.sha384(password).hexdigest()
	sha_512 = hashlib.sha512(password).hexdigest()
	sha_extreme = sha_256 + sha_384 + sha_512
	sha_finger = chop(sha_extreme, 96)
	return drunken_bishop_merge(sha_finger)


def drunken_bishop_unused(password):
	password = password.encode('utf-8')
	sha_160 = hashlib.sha1(password).hexdigest()
	sha_224 = hashlib.sha224(password).hexdigest()
	sha_unused = sha_160 + sha_224
	sha_finger = chop(sha_unused, 32)
	return drunken_bishop_merge(sha_finger)


################################################################################


from random import randint, shuffle
def password_gen(total, upcase, lowcase, numbers, others = 0, characters = ''):
	assert isinstance(total, int)
	assert isinstance(upcase, int)
	assert isinstance(lowcase, int)
	assert isinstance(numbers, int)
	assert isinstance(others, int)
	assert isinstance(characters, str)
	assert total >= ( upcase + lowcase + numbers + others )
	up_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	low_char = 'abcdefghijklmnopqrstuvwxyz'
	num_char = '0123456789'
	characters = '+-_=.:/' if characters == '' else characters
	characters = characters
	royale = up_char + low_char + num_char + characters
	result = ''
	for i in range(upcase):
		result += up_char[randint(0, 25)]
	for i in range(lowcase):
		result += low_char[randint(0, 25)]
	for i in range(numbers):
		result += num_char[randint(0, 9)]
	for i in range(others):
		result += characters[randint(0, len(characters)-1)]
	for i in range(total - upcase - lowcase - numbers - others):
		result += royale[randint(0, len(royale)-1)]
	result = list(result)
	shuffle(result)
	return ''.join(result)