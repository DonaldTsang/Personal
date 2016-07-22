# https://github.com/aberaud/base91-python/blob/master/base91.py
# https://github.com/thenoviceoof/base92/blob/master/python/base92/base92.py
# 256MiBytes / 13Bytes * 16 characters = 330,382,100 characters (round up)

from struct import pack, unpack

b91_alph = [
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
	'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
	'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
	'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '#', '$',
	'%', '&', '(', ')', '*', '+', ',', '.', '/', ':', ';', '<', '=',
	'>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', '"']

de_table = dict((v,k) for k,v in enumerate(b91_alph))

def decode(en_str): #Decode Base91 string to a bytearray
	v, b, n = -1, 0, 0
	out = bytearray()
	for strletter in en_str:
		if not strletter in de_table: continue
		c = de_table[strletter]
		if(v < 0): v = c
		else:
			v += c * 91
			b |= v << n
			n += 13
			while True:
				out += pack('B', b&255)
				b >>= 8
				n -= 8
				if not n>7: break
			v = -1
	if v+1: out += pack('B', (b | v << n) & 255 )
	return bytes(out)

def encode(bindata): # Encode a bytearray to a Base91 string
	b, n = 0, 0
	out = ''
	for count in range(len(bindata)):
		byte = bindata[count:count+1]
		b |= unpack('B', byte)[0] << n
		n += 8
		if n>13:
			v = b & 8191
			b >>= 13
			n -= 13
			out += b91_alph[v % 91] + b91_alph[v // 91]
	if n:
		out += b91_alph[b % 91]
		if n>7 or b>90: out += b91_alph[b // 91]
	return out
