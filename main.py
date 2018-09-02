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
		mods = []
		i = -1
		marks = {}
		for k in self.keys:
			i += 1
			simidx.append(0)
			for tag in tags:
				if tag[0] != '$' and tag in k:
					simidx[i] += 1
				elif tag[0] == '$':
					mods.append(tag)
			for tag in veto:
				if tag in k:
					simidx[i] -= 5
					
		m = maxindices(simidx)
		print(simidx)
		#if len(maxindices(simidx)) > 1: raise ValueError("Given tags are too ambiguous")
		w = random.choice(m)
		print(m)
		return self.vals[w], mods

lemmas = LemmaDB(keys, vals)


class GrammarDB:
	def __init__(self):
		self.templates = {}

	def add_template(self, _type, *definitions):
		if self.templates.get(_type) is None:
			self.templates[_type] = []
		self.templates[_type] += definitions

	def get_template(self, _type):
		return random.choice(self.templates[_type])

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
	else:
		defs.append(line)

if t:
	grammar.add_template(t, *defs)

# print(grammar.get_template('NOUN'))

class Word:
	def __init__(self, tags, modifiers=[]):
		self.word, self.mods = lemmas.get_closest(*tags)
		self.tags = lemmas.get_word(self.word)
		self.mods += modifiers

	def modify(self, mod):
		self.mods.append(mod)

	def render(self):
		return self.word

class Block:
	def __init__(self, name):
		self.name = name
		self.words = [Word(word.split('+')) for word in grammar.get_template(name).split(' ')]

	def render(self):
		return ' '.join([w.render() for w in self.words])

print(Block('NOUN').render())
