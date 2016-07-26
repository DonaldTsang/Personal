# https://github.com/aberaud/base91-python/blob/master/base91.py
# https://github.com/thenoviceoof/base92/blob/master/python/base92/base92.py
# 256*(1024^2)Bytes / 13Bytes * 16char = 330,382,100char (round-up)
# Every 13Bytes can be converted into 16char in base91

b91_alph = [
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
	'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
	'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
	'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '#', '$',
	'%', '&', '(', ')', '*', '+', ',', '.', '/', ':', ';', '<', '=',
	'>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', '"']

de_table = dict((v,k) for k,v in enumerate(b91_alph))

def en(bindata): # Encode a bytes to a Base91 string
	from struct import unpack
	b, n = 0, 0
	out = ''
	for count in range(len(bindata)):
		byte = bindata[count:count+1]
		b |= unpack('B', byte)[0] << n; n += 8
		if n > 13:
			v = b & 8191; b >>= 13; n -= 13
			out += b91_alph[v % 91] + b91_alph[v // 91]
	if n:
		out += b91_alph[b % 91]
		if n > 7 or b > 90: out += b91_alph[b // 91]
	return out

def de(en_str): # Decode Base91 string to bytes
	from struct import pack
	v, b, n = -1, 0, 0
	out = bytearray()
	for strletter in en_str:
		if not strletter in de_table: continue
		c = de_table[strletter]
		if v < 0: v = c
		else:
			v += c * 91; b |= v << n; n += 13
			while True:
				out += pack('B', b&255)
				b >>= 8; n -= 8
				if not n > 7: break
			v = -1
	if v + 1: out += pack('B', (b | v << n) & 255)
	return bytes(out)

def b91_en(inputs, output):
	i = open(inputs, "rb")
	o = open(output, "wb")
	o.write(b'testing pages (encode)')
	i.close(); o.close()

def b91_de(inputs, output):
	i = open(inputs, "rb")
	o = open(output, "wb")
	o.write(b'testing pages (decode)')
	i.close(); o.close()

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='base91 file conversion')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-e", "--encode", action="store_true", 
		help="Encode binaries into base91 text file")
	group.add_argument("-d", "--decode", action="store_true", 
		help="Decode base91 text file into binaries")
	parser.add_argument("inputs", type=open,
		help="the inputs file name")
	parser.add_argument("output", type=open,
		help="the output file name")
	args = parser.parse_args()
	if args.encode: b91_en(args.inputs, args.output)
	elif args.decode: b91_de(args.inputs, args.output)
