def maxindices(lst):
	maxes = []
	m = 0
	i = 0
	for item in lst:
		if item > m:
			m = item
			maxes = [i]
		elif item == m:
			maxes.append(i)
		i += 1
	return maxes