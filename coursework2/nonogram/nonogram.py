import os, sys
from cnf import to_cnf, _to_minisat

'''
CS402 Coursework 2 - Nonogram solver
20140515 Sungyoon Jeong
   ______________
  /             /|
 /             / |
/_____________/  |
|             |  /
|   O  O  O   | /
|_____________|/

This is a box.
The nonogram solver you asked for is inside.
'''

# Check validity of input file.
def check_validity(input_fname):
	try:
		f = open(input_fname, 'r')
		row = int(f.readline().strip())
		col = int(f.readline().strip())
		for i in xrange(row):
			if minlen(map(int, f.readline().strip().split(' '))) > col:
				f.close()
				return False
		for i in xrange(col):
			if minlen(map(int, f.readline().strip().split(' '))) > row:
				f.close()
				return False
		f.close()
		return True
	except IOError:
		print "Error: File does not exist"
		return False
	except ValueError:
		print "Error: Invalid input in input file"
		return False

# Calculate minimal length of clues.
def minlen(l):
	s = 0
	for i in l:
		if i < 0:
			raise ValueError
		if i == 0:
			if len(l) == 1:
				return 0
			else:
				raise ValueError
		s += (i + 1)
	s -= 1
	return s

# Wrapper function, just to make cumulating easier.
def add(left, right, op):
	if left and right:
		return (op, left, right)
	else:
		return left or right

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: python cnf.py inputfile"
		exit()
	if not check_validity(sys.argv[1]):
		exit()

	f_in = open(sys.argv[1], 'r')

	row = int(f_in.readline().strip())
	col = int(f_in.readline().strip())

	row_clues = []
	col_clues = []
	literal = []
	nonogram_formula = None

	for r in xrange(row):
		row_clues.append(map(int, f_in.readline().strip().split(' ')))
	for c in xrange(col):
		col_clues.append(map(int, f_in.readline().strip().split(' ')))

	# print "Step 1: Making nonogram into logical formula"
	for r in range(row):
		row_clue = row_clues[r]
		if minlen(row_clue) == 0:
			and_st = None
			for j in xrange(col):
				literal.append('R%d_%d_%d' % (r, 0, j))
				and_st = add(and_st, ('-', 'R%d_%d_%d' % (r, 0, j)), '&')
				and_st = add(and_st, ('-', 'X%d_%d' % (r, j)), '&')
			nonogram_formula = add(nonogram_formula, and_st, '&')
		else:
			chunk_cumulative = 0
			entropy = col - minlen(row_clue) + 1
			for i in xrange(len(row_clue)):
				and_st = None
				or_st = None
				for j in xrange(col):
					row_chunk_literal = 'R%d_%d_%d' % (r, i, j)
					literal.append(row_chunk_literal)
					if (j >= chunk_cumulative) and (j < chunk_cumulative + entropy):
						or_st = add(or_st, row_chunk_literal, '|')
					else:
						and_st = add(and_st, ('-', row_chunk_literal), '&')
				and_st = add(and_st, or_st, '&')

				for j in xrange(chunk_cumulative, chunk_cumulative + entropy):
					temp_st = None
					for k in xrange(col):
						if k != j:
							temp_st = add(temp_st, ('-', 'R%d_%d_%d' % (r, i, k)), '&')
					if i != len(row_clue) - 1:
						for k in xrange(0, j + row_clue[i] + 1):
							temp_st = add(temp_st, ('-', 'R%d_%d_%d' % (r, i+1, k)), '&')
					for k in xrange(j, j + row_clue[i]):
						temp_st = add(temp_st, 'X%d_%d' % (r, k), '&')
					temp_st = ('>', 'R%d_%d_%d' % (r, i, j), temp_st)
					and_st = add(temp_st, and_st, '&')
				chunk_cumulative += row_clue[i] + 1
				nonogram_formula = add(nonogram_formula, and_st, '&')

	for c in range(col):
		col_clue = col_clues[c]
		if minlen(col_clue) == 0:
			and_st = None
			for j in xrange(row):
				literal.append('C%d_%d_%d' % (c, 0, j))
				and_st = add(and_st, ('-', 'C%d_%d_%d' % (c, 0, j)), '&')
				and_st = add(and_st, ('-', 'X%d_%d' % (j, c)), '&')
			nonogram_formula = add(nonogram_formula, and_st, '&')
		else:
			chunk_cumulative = 0
			entropy = row - minlen(col_clue) + 1
			for i in xrange(len(col_clue)):
				and_st = None
				or_st = None
				for j in xrange(row):
					col_chunk_literal = 'C%d_%d_%d' % (c, i, j)
					literal.append(col_chunk_literal)
					if (j >= chunk_cumulative) and (j < chunk_cumulative + entropy):
						or_st = add(or_st, col_chunk_literal, '|')
					else:
						and_st = add(and_st, ('-', col_chunk_literal), '&')
				and_st = add(and_st, or_st, '&')

				for j in xrange(chunk_cumulative, chunk_cumulative + entropy):
					temp_st = None
					for k in xrange(row):
						if k != j:
							temp_st = add(temp_st, ('-', 'C%d_%d_%d' % (c, i, k)), '&')
					if i != len(col_clue) - 1:
						for k in xrange(0, j + col_clue[i] + 1):
							temp_st = add(temp_st, ('-', 'C%d_%d_%d' % (c, i+1, k)), '&')
					for k in xrange(j, j + col_clue[i]):
						temp_st = add(temp_st, 'X%d_%d' % (k, c), '&')
					temp_st = ('>', 'C%d_%d_%d' % (c, i, j), temp_st)
					and_st = add(temp_st, and_st, '&')
				chunk_cumulative += col_clue[i] + 1
				nonogram_formula = add(nonogram_formula, and_st, '&')

	for r in range(row):
		for c in range(col):
			literal.append('X%d_%d' % (r, c))
			row_st = None
			col_st = None
			for i in xrange(len(row_clues[r])):
				if row_clues[r][i] == 0:
					break
				start = max(0, c - row_clues[r][i] + 1)
				end = min(c, col - row_clues[r][i])
				for j in xrange(start, end + 1):
					row_st = add(row_st, 'R%d_%d_%d' % (r, i, j), '|')
			for i in xrange(len(col_clues[c])):
				if col_clues[c][i] == 0:
					break
				start = max(0, r - col_clues[c][i] + 1)
				end = min(r, row - col_clues[c][i])
				for j in xrange(start, end + 1):
					col_st = add(col_st, 'C%d_%d_%d' % (c, i, j), '|')
			pixel_st = add(row_st, col_st, '&')
			if pixel_st:
				nonogram_formula = add(nonogram_formula, ('>', 'X%d_%d' % (r, c), pixel_st), '&')

	# print "Step 2: Converting to cnf form..."
	nonogram_formula = to_cnf(nonogram_formula)

	with open('minisat_in', 'w') as f:
		f.write('p cnf %d %d\n' % (len(literal), str(nonogram_formula).count('&') + 1))
		f.write(_to_minisat(nonogram_formula, literal))
		f.write(' 0')
		f.close()

	# print "Step 3: Using minisat to solve formula..."
	os.system("minisat %s %s > /dev/null" % ('minisat_in', 'minisat_out'))
	with open('minisat_out', 'r') as out:
		sat = out.readline().strip()
		if sat == "UNSAT":
			print "Error: Unsatisfiable nonogram"
			exit()
		res = out.readline().strip().split(' ')

	for r in range(row):
		row_str = ""
		for c in range(col):
			pix_idx = literal.index('X%d_%d' % (r, c)) + 1
			if str(pix_idx) in res:
				row_str += '#'
			elif '-' + str(pix_idx) in res:
				row_str += '.'
		print row_str
