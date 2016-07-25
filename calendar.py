def calendar(year, month, day):
	assert isinstance(year, int)
	assert isinstance(month, int)
	assert year >= 1935, "Fuhrer error"
	assert 1 <= month <= 12, "month error"
	if month in [1, 3, 5, 7, 8, 10, 12]:
		assert 1 <= day <= 31, "day error"
	elif month in [4, 6, 9, 11]:
		assert 1 <= day <= 30, "day error"
	elif month == 2: # Gregorian calendar
		if year % 400 == 0:
			assert 1 <= day <= 29, "day error"
		elif year % 100 == 0:
			assert 1 <= day <= 28, "day error"
		elif year % 4 == 0:
			assert 1 <= day <= 29, "day error"
		elif year % 4 != 0:
			assert 1 <= day <= 28, "day error"

	if month == 12 and day > 20: year += 1; month = 0; day -= 20
	if month == 2 and day == 29: return [year, 'leaps','l', 'l']
	elif month == 8 and day == 30: return [year, 'earth', 'e', 'e']
	elif month == 8 and day == 31: return [year, summer, 11, 1]
	if month < 8 or (month == 8 and day < 30):
		day_count = [0, 11, 42, 70, 101, 131, 162, 192, 223][month] + day - 1
	if month > 8:
		day_count = [1, 31, 62, 92][month - 9] + 252 + day - 1
	season, day_count = divmod(day_count, 91)
	week_count, day_count = divmod(day_count, 7)
	season = ["winter", "spring", "summer", "autumn"][season]
	week_count += 1; day_count += 1
	return [year, season, week_count, day_count]
