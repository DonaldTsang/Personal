def date(month, day):
	assert 0 < month <= 13, "month out of bound"
	assert 0 < day <= 30, "day out of bound"
	char = "一二三四五六七八九十廿卅卌"[month - 1]
	if day % 10 == 0:
		return char + "初二三"[day // 10 - 1] + "十"
	else:
		return char + "初十廿"[day // 10] + \
		"一二三四五六七八九"[day % 10 - 1]
