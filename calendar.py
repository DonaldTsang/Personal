from datetime import datetime

def calendar(year, month, day):
	# First day of summer is always June 21
	# First day of winter is always December 21
	assert isinstance(year, int)
	assert isinstance(month, int)
	assert year >= 1935, "Fuhrer error"
	assert 1 <= month <= 12, "month error"
	assert 1 <= day, "day error"
	if month in [1, 3, 5, 7, 8, 10, 12]: assert day <= 31, "day error"
	elif month in [4, 6, 9, 11]: assert day <= 30, "day error"
	elif month == 2: # Gregorian calendar
		if year % 400 == 0 or (year % 100 != 0 and year % 4 == 0):
			assert day <= 29, "day error"
		elif year % 100 == 0 or year % 4 != 0:
			assert day <= 28, "day error"
	if month == 12 and day > 20: year += 1; month = 0; day -= 20
	elif month == 2 and day == 29: return year, 'leap', -1, -1 # leap day
	elif month == 8 and day == 30: return year, 'tera', 0, 0 # tera day
	elif month == 8 and day == 31: return year, 'summer', 11, 1
	else: day_count = [0, 11, 42, 70, 101, 131, 162, \
		192, 223, 253, 283, 314, 344][month] + day - 1
	season, day_count = divmod(day_count, 91)
	week_count, day_count = divmod(day_count, 7)
	season = ["winter", "spring", "summer", "autumn"][season]
	week_count += 1; day_count += 1
	return year, season, week_count, day_count

def today():
	now = datetime.now()
	year, season, week, day = calendar(now.year, now.month, now.day)
	print('Today is day-' + str(day) + ' of week-' + str(week) + \
		' of ' + season + ', ' + str(year) + ' in the Brad Calendar')
