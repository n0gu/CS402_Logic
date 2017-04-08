'''
CS402 Coursework 2 - CNF
20140515 Sungyoon Jeong
'''

import sys, os, subprocess
op = ['&', '|', '-', '>', '<', '=']

'''
Take polish notation boolean formula as input, and make a tuple with it.
Tuple consists of (op, lit, lit) or (op, lit) where type(lit) is tuple or string.
'''
def perror():
	print "Error while parsing... exiting!"
	exit()

def parse_formula(formula):
	res, rest = _parse(formula.split(' '))
	if rest:
		perror()
	return res

def _parse(formula_split):
	if len(formula_split) == 0:
		perror()
	if formula_split[0] == '-':
		lit, rest = _parse(formula_split[1:])
		return ((formula_split[0], lit), rest)
	elif formula_split[0] in op:
		lit1, rest1 = _parse(formula_split[1:])
		lit2, rest2 = _parse(rest1)
		return ((formula_split[0], lit1, lit2), rest2)
	else:
		return (formula_split[0], formula_split[1:])

'''
All these functions take tuples as input parameter.
'''
def eqfree(formula):
	if formula[0] not in op:
		return formula
	elif formula[0] == '=':
		return ('&', ('>', eqfree(formula[1]), eqfree(formula[2])), ('<', eqfree(formula[1]), eqfree(formula[2])))
	elif formula[0] == '-':
		return ('-', eqfree(formula[1]))
	elif formula[0] in op:
		return (formula[0], eqfree(formula[1]), eqfree(formula[2]))
	else:
		print "Should not arrive here"

def revimplfree(formula):
	if formula[0] not in op:
		return formula
	elif formula[0] == '<':
		return ('>', revimplfree(formula[2]), revimplfree(formula[1]))
	elif formula[0] == '-':
		return ('-', revimplfree(formula[1]))
	elif formula[0] in op:
		return (formula[0], revimplfree(formula[1]), revimplfree(formula[2]))
	else:
		print "Should not arrive here"

def implfree(formula):
	if formula[0] not in op:
		return formula
	elif formula[0] == '>':
		return ('|', implfree(('-', formula[1])), implfree(formula[2]))
	elif formula[0] == '-':
		return ('-', implfree(formula[1]))
	elif formula[0] in op:
		return (formula[0], implfree(formula[1]), implfree(formula[2]))
	else:
		print "Should not arrive here"

def nnf(formula):
	if formula[0] not in op:
		return formula
	elif formula[0] == '-':
		if formula[1][0] == '-':
			return nnf(formula[1][1])
		elif formula[1][0] == '&':
			return nnf(('|', ('-', formula[1][1]), ('-', formula[1][2])))
		elif formula[1][0] == '|':
			return nnf(('&', ('-', formula[1][1]), ('-', formula[1][2])))
		else:
			return formula
	elif formula[0] == '&' or formula[0] == '|':
		return (formula[0], nnf(formula[1]), nnf(formula[2]))
	else:
		print "Should not arrive here"

def cnf(formula):
	if formula[0] not in op or formula[0] == '-':
		return formula
	elif formula[0] == '&':
		return ('&', cnf(formula[1]), cnf(formula[2]))
	elif formula[0] == '|':
		return distr(cnf(formula[1]), cnf(formula[2]))
	else:
		print "Should not arrive here"

def distr(f1, f2):
	if f1[0] == '&':
		return ('&', distr(f1[1], f2), distr(f1[2], f2))
	elif f2[0] == '&':
		return ('&', distr(f1, f2[1]), distr(f1, f2[2]))
	else:
		return ('|', f1, f2)

# Wrapper function
def to_cnf(formula):
	return cnf(nnf(implfree(revimplfree(eqfree(formula)))))

'''
Print tuple into various output formats
'''
def cnf_to_polish(formula):
	magic = str(formula)
	return magic.replace('(', '').replace(')', '').replace('\'', '').replace(',', '')

def cnf_to_infix(formula):
	if formula[0] == '&':
		left = '(%s)' % cnf_to_infix(formula[1]) if formula[1][0] == '|' else cnf_to_infix(formula[1])
		right = '(%s)' % cnf_to_infix(formula[2]) if formula[2][0] == '|' else cnf_to_infix(formula[2])
		return '%s & %s' % (left, right)
	elif formula[0] == '-':
		return '- %s' % formula[1]
	elif formula[0] == '|':
		return '%s | %s' % (cnf_to_infix(formula[1]), cnf_to_infix(formula[2]))
	else:
		return formula

def cnf_to_minisat(formula, in_filename):
	lits = set()
	magic = cnf_to_polish(formula).split(' ')
	for c in magic:
		if c not in op:
			lits.add(c)
	lits = list(lits)
	lits.sort()

	with open(in_filename, 'w') as f:
		f.write('p cnf %d %d\n' % (len(lits), magic.count('&') + 1))
		f.write(_to_minisat(formula, lits))
		f.write(' 0')

def _to_minisat(formula, lits):
	if formula[0] == '&':
		return _to_minisat(formula[1], lits) + ' 0\n' + _to_minisat(formula[2], lits)
	elif formula[0] == '|':
		return _to_minisat(formula[1], lits) + ' ' +  _to_minisat(formula[2], lits)
	elif formula[0] == '-':
		return '-' + _to_minisat(formula[1], lits)
	else:
		return str(lits.index(formula) + 1)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: python cnf.py prop_formula"
		exit()
	formula = parse_formula(sys.argv[1].strip())
	formula = to_cnf(formula)
	print cnf_to_polish(formula)
	print cnf_to_infix(formula)

	minisat_input = "test.in"
	minisat_output = "test.out"
	cnf_to_minisat(formula, minisat_input)
	result = os.system("minisat %s %s > /dev/null" % (minisat_input, minisat_output))
	with open(minisat_output, 'r') as out:
		sat = out.readline().strip()
	if sat == "SAT":
		print "Valid"
	else:
		print "Not Valid"