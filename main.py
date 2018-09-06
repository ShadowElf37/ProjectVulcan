from lib import *
import random

vowels = 'aeiouy'
consonants = 'bcdfghjklmnpqrstvwxz'

data = open('lemmas.txt').read()
_taglist = open('tags.txt').read().split('+++')
taglist2 = open('tags.txt').read().split('\n')
taglist = []
for i in _taglist:
	temp = []
	tags = i.split('\n')
	for item in tags:
		if item:
			temp.append(item)
	taglist.append(temp)

tlsort = lambda x: taglist2.index(x)

# LOAD lemmas.txt
keys = []
vals = []
tags = []
for line in data.split('\n'):
	if not line or line[0] == '#':
		continue

	elif line[:2] == '::':
		l = line[2:]
		t = ''
		p = 0
		for char in l:
			if char in '+-' and t:
				if p == 1:
					tags.append(t)
				elif p == 0:
					if t == 'ALL':
						tags = []
					else:
						tags.remove(t)
				t = ''

			if char == '+':
				p = 1
			elif char == '-':
				p = 0
			else:
				t += char

		if p == 1:
			tags.append(t)
		elif p == 0:
			if t == 'ALL':
				tags = []
			else:
				tags.remove(t)
		t = ''
		
		tags.sort(key=tlsort)

	else:
		l = line.split('|')
		newtags = []
		if len(l) != 1:
			newtags = l[1].strip().split(',')
		keys.append(tuple(sorted((tags + newtags), key=tlsort)))
		vals.append(l[0].strip())

class LemmaDB:
	def __init__(self, descriptors, words):
		self.keys = descriptors
		self.vals = words

	def get_word(self, s):
		return self.keys[self.vals.index(s)]
	def get_closest(self, *tags, veto=[]):
		simidx = []
		i = -1
		marks = {}
		for k in self.keys:
			i += 1
			simidx.append(0)
			for tag in tags:
				if tag in k:
					simidx[i] += 1
			for tag in veto:
				if tag in k:
					simidx[i] -= 5
					
		m = maxindices(simidx)
		#print(simidx)
		#if len(maxindices(simidx)) > 1: raise ValueError("Given tags are too ambiguous")
		w = random.choice(m)
		#print(m)
		return self.vals[w]

lemmas = LemmaDB(keys, vals)


class GrammarDB:
	def __init__(self):
		self.templates = {}

	def add_template(self, _type, *definitions):
		if self.templates.get(_type) is None:
			self.templates[_type] = []
		self.templates[_type] += definitions

	def get_template(self, _type):
		t = random.choice(self.templates[_type])
		return t

# READ grammar.txt
grammardata = open('grammar.txt').read().split('\n')
grammar = GrammarDB()
t = ''
defs = []
for line in grammardata:
	if not line or line[0] == '#':
		continue
	elif line[0] == '!':
		if t:
			grammar.add_template(t, *defs)
		t = line[1:]
		defs = []
	else:
		defs.append(line)

if t:
	grammar.add_template(t, *defs)

# print(grammar.get_template('NOUN'))

class Word:
	def __init__(self, tags, parent):
		self.parent = parent
		self.mods = [tag[1:] for tag in tags if tag[0] == '$']
		self.tags = [tag for tag in tags if tag[0] != '$']
		self.word = lemmas.get_closest(*tags)
		self.tags = lemmas.get_word(self.word)

	def modify(self, mod):
		self.mods.append(mod)

	def render(self):
		return self.word

	def __repr__(self):
		return self.word

class Block:
	def __init__(self, name, parent=None, dup=False):
		self.parent = parent
		self.name = name
		self.words = []
		self.template = grammar.get_template(name).split(' ')
		#print(self.template)
		for word in self.template:
			repeat = 1
			optional = 1
			i = -1
			for char in word:
				i += 1
				if char == '#':
					repeat += 1
				elif char == '?':
					optional = 0
				else:
					sidx = i
					break
			if word[sidx] == '.':
				for i in range(random.randint(optional,repeat)):
					self.words.append(Block(word[sidx+1:], self, dup=False))
			else:
				self.words.append(Word(word.split('+'), self))
		#self.words = [Word(word.split('+')) if word[0] != '.' else Block(word[1:]) for word in grammar.get_template(name).split(' ')]

	def render(self):
		#print(self.words)
		return ' '.join([w.render() for w in self.words])

	def __repr__(self):
		return self.name+' <'+str(self.words)+'>'

class ConjugationDB:
	def __init__(self):
		self.table = {}

	def add_conjugation(self, _type, conj):
		self.table[_type] = conj

	def get_closest(self, attributes):
		keys = self.table.keys()
		simidx = [0]*len(keys)
		i = -1
		for key in keys:
			i += 1
			for tag in attributes:
				if tag in key:
					simidx[i] += 1
		t = self.table[keys[random.choice(maxindices(simidx))]]
		return t

conjugations = ConjugationDB()

cf = open('conjugation.txt').read().split('\n')
for line in cf:
	if not line or line[0] == '#':
		continue
	else:
		q,conj = line.split('=')
		q = q.strip()
		conj = conj.strip()
		conjugations.add_conjugation(q, conj)

# Conjugations are accessed via closest match
# No parsing implemented yet, so @ and $ are literal

while True:
	input('\n'+Block('CLAUSE').render())

