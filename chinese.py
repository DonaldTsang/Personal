def date(month, day):
	assert 0 < month <= 13, "month out of bound"
	assert 0 < day <= 30, "day out of bound"
	char = "一二三四五六七八九十廿卅卌"[month - 1]
	if day % 10 == 0:
		alphabet = "初二三"
		return char + alphabet[day // 10 - 1] + "十"
	else:
		alph_10 = "初十廿"
		alph_01 = "一二三四五六七八九"
		key = day // 10
		return char + alph_10[key] + alph_01[day % 10 - 1]
