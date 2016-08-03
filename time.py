from time import time, sleep
from datetime import datetime
from math import floor

characters = "0123456789ABCDEFGHIJ"

def current_time_microsecond():
	now = datetime.now().time()
	mega = 10 ** 6
	return (now.hour*mega*60*60)+(now.minute*mega*60)+(now.second*mega)+(now.microsecond)

def base(num, base):
	assert isinstance(num, int), "Error: number is not integer"
	assert isinstance(base, int), "Error: base is not integer"
	assert num >= 0, "Error: number is negative"
	assert 2 <= base <= 20, "Error: base out of range"
	return characters[num//base] + characters[num%base]

def current_time_special(time, x):
	assert type(time) is int, "Error: time is not integer"
	assert type(x) is int, "Error: x is not integer"
	assert  2 <= x <= 20, "Error: x out of range"
	c = ( 10 ** 6 ) * ( 60 ** 2 ) * 24
	hour = (time*(x**1))//c
	minute = (time*(x**3))//c-hour*(x**2)
	second = (time*(x**5))//c-hour*(x**4)-minute*(x**2)
	return base(hour, x)[1] + ':' + base(minute, x) + ':' + base(second, x)

def current_time():
	time = current_time_microsecond()
	return 'Decimal---' + current_time_special(time, 10) + '\n' + \
		'Dozenal---' + current_time_special(time, 12) + '\n' + \
		'HexTime---' + current_time_special(time, 16) + '\n' + \
		'Vigesimal-' + current_time_special(time, 20) 

def clock_time():
	end_time = time() + 5
	while time() < end_time:
		print(current_time(), end='\r\033[3A')
	print('\033[4B')

if __name__ == '__main__':
	clock_time()
