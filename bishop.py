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
ROOM_DIMENSIONS = (STARTING_POSITION[0] * 2 + 1, STARTING_POSITION[1] * 2 + 1)

# encode start and end positions
COIN_VALUE_STARTING_POSITION, COIN_VALUE_ENDING_POSITION = 15, 16

BORDER = '+' + '-' * ROOM_DIMENSIONS[0] + '+\n'

def hex_byte_to_binary(hex_byte): # Convert hex byte into a string of bits
    assert len(hex_byte) == 2
    return bin(int(hex_byte, 16))[2:].zfill(8)

def bit_pairs(binary): # Convert a word into bit pairs little-endian style.
    def take(n, iterable):
        "Return first n items of the iterable as a list"
        return list(itertools.islice(iterable, n))
    def all_pairs(iterable):
        while True:
            pair = take(2, iterable)
            if not pair: break
            yield ''.join(pair)
    return list(reversed(list(all_pairs(iter(binary)))))

class Direction(object):
    """Encode a sense of direction."""
    def __init__(self, dx, dy):
        self.dx, self.dy = dx, dy

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

import re

def db_fix(fingerprint):
	if bool(re.fullmatch('([0-9A-Fa-f]{2}[:]){0,}[0-9A-Fa-f]{2}', fingerprint)):
		return fingerprint
	elif bool(re.fullmatch('([0-9A-Fa-f]{2}){1,}', fingerprint)):
		result = ""
		for i in range(len(fingerprint) // 2):
			result += (fingerprint[2*i:2*i+2] + ':')
		return result[:-1]
	else: assert False, "Error: fingerprint is invalid"

def db(fingerprint): # Creates a piece of art base on 32 hex
	fingerprint = db_fix(fingerprint)
	room = stumble_around(fingerprint)
	return display_room(room)

def db_tops(fingerprint): # db but without the bottom frame
	fingerprint = db_fix(fingerprint)
	room = stumble_around(fingerprint)
	return display_room(room)[:-(ROOM_DIMENSIONS[0]+3)]

def chop(string, length): # chop string into blocks
	return [string[i:i+length] for i in range(0, len(string), length)]

def db_multiple(fingerprint): # Vertically stacked drunken_bishop
	fingerprint = db_fix(fingerprint)
	finger = [i.rstrip(':') for i in chop(fingerprint, 48)]
	picture = [db_tops(i) for i in finger]
	return ''.join(picture) + BORDER

################################################################################

import hashlib

def db_scrape(fingerprint):
	room = db_multiple(fingerprint)
	scan = room.split('\n')[:-1]
	return [item[:-1] for item in scan]

def db_merge(list):
	super_list = []
	for item in list:
		super_list.append(db_scrape(item))
	output = [''] * len(super_list[0])
	for y in range(len(super_list[0])):
		for x in range(len(super_list)):
			output[y] += super_list[x][y]
		output[y] += output[y][0]
	return '\n'.join(output) + '\n'

def db_1x1(passwd): # A 1x1 db rectangle based on MD-5
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	md5 = hashlib.md5(passwd).hexdigest()
	return db_merge(chop(md5, 32))

def db_1x2(passwd): # A 1x2 db rectangle based on SHA-256
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	sha_256 = hashlib.sha256(passwd).hexdigest()
	return db_merge(chop(sha_256, 32))

def db_1x3(passwd): # A 1x3 db rectangle based on SHA-384
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	sha_384 = hashlib.sha384(passwd).hexdigest()
	return db_merge(chop(sha_384, 32))

def db_2x2(passwd): # A 2x2 db rectangle based on SHA-512
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	sha_512 = hashlib.sha512(passwd).hexdigest()
	return db_merge(chop(sha_512, 64))

def db_2x3(passwd): # A 2x3 db rectangle based on SHA-256/512
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	sha_256 = hashlib.sha256(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	sha_finger = sha_256 + sha_512
	return db_merge(chop(sha_finger, 64))

def db_2x4(passwd): # A 2x3 db rectangle based on MD5 & SHA-384/512
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	md5 = hashlib.md5(passwd).hexdigest()
	sha_384 = hashlib.sha384(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	sha_finger = md5 + sha_384 + sha_512
	return db_merge(chop(sha_finger, 64))

def db_3x3(passwd): # A 3x3 db rectangle based on SHA-256/384/512
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	sha_256 = hashlib.sha256(passwd).hexdigest()
	sha_384 = hashlib.sha384(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	sha_finger = sha_256 + sha_384 + sha_512
	return db_merge(chop(sha_finger, 96))

################################################################################

def db_ded(passwd):
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	sha_160 = hashlib.sha1(passwd).hexdigest()
	sha_224 = hashlib.sha224(passwd).hexdigest()
	sha_unused = sha_160 + sha_224
	return db_merge(chop(sha_unused, 32))

def db_wow(passwd):
	passwd = passwd.encode('utf-8') if isinstance(passwd, str) else passwd
	sha_256 = hashlib.sha256(passwd).hexdigest()
	sha_384 = hashlib.sha384(passwd).hexdigest()
	sha_512 = hashlib.sha512(passwd).hexdigest()
	sha_160 = hashlib.sha1(passwd).hexdigest()
	sha_224 = hashlib.sha224(passwd).hexdigest()
	sha_finger = sha_256 + sha_384 + sha_512 + (sha_160 + sha_224)
	return db_merge(chop(sha_finger, 96))

################################################################################

from random import randint, shuffle

def passwd_gen(total, upcase, lowcase, numbers, others = 0, chars = ''):
	assert isinstance(total, int) and total > 0
	assert isinstance(upcase, int) and upcase > 0
	assert isinstance(lowcase, int) and lowcase > 0
	assert isinstance(numbers, int) and numbers > 0
	assert isinstance(others, int) and others > 0
	assert isinstance(chars, str)
	assert total >= ( upcase + lowcase + numbers + others )
	up_char = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	low_char = 'abcdefghijklmnopqrstuvwxyz'
	num_char = '0123456789'
	chars = '+-_=.:/' if chars == '' else chars
	royale = up_char + low_char + num_char + chars
	rest = total - upcase - lowcase - numbers - others
	result = ''
	for i in range(upcase): result += up_char[randint(0, 25)]
	for i in range(lowcase): result += low_char[randint(0, 25)]
	for i in range(numbers): result += num_char[randint(0, 9)]
	for i in range(others): result += chars[randint(0, len(chars)-1)]
	for i in range(rest): result += royale[randint(0, len(royale)-1)]
	result = list(result)
	shuffle(result)
	return ''.join(result)
