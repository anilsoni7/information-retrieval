import re
import os
from collections import defaultdict
from nltk import word_tokenize
from nltk.corpus import stopwords

import pprint
import sys
import cProfile, pstats, io


class Operator:

	@staticmethod
	def intersection(result,term):
		#print(term)
		return result.intersection(term)

	@staticmethod
	def union(result, term):
		return result.union(term)

	@staticmethod
	def compliment(result, term):
		#print(term)
		return result.difference(term)



class BooleanQuery:
	
	OPERATORS = {	'and' : Operator.intersection,
			'or' : Operator.union,
			'not': Operator.compliment
		} 
	#operators_initials = ['A','O','N']
	def __init__(self,InvertedIndexObject):
		self.InvertedIndexObject = InvertedIndexObject
		self.reg = re.compile( "( and | or )" )
		
	def Tokenize(self,query):
		return self.reg.split(query)

	def search(self, query):
		query = [x.strip()  for x in  self.Tokenize(query.lower())]
		query.reverse()
		#print("final query :: ",query)
		term = query.pop()
		compliment = set()
		result=set()
		#print(query)
		#Base exception 
		if "not" in term:
			# sclice the temr eg NOT drug => drug
			#print(term , self.InvertedIndexObject.get_posting(term) )
			#print("compliment :: ",term)			
			compliment.update( self.InvertedIndexObject.get_posting(term[4:]) )
			#print(compliment)
		else:
			#print(term , self.InvertedIndexObject.get_posting(term), "AND | OR" )
			#assert self.InvertedIndexObject.get_posting(term) is not None
			#print(self.InvertedIndexObject.__contains__(term))

			if self.InvertedIndexObject.inverted_index.__contains__(term):
				result.update( self.InvertedIndexObject.get_posting(term))
		#print("query",query, result)
			
		try:
			while True:
				term = query.pop()
				if "not" in term:
					#term = term[4:]	# sclice the temr eg NOT drug => drug
					#print("compliment :: ",term)
					compliment.update( self.InvertedIndexObject.get_posting(term[4:].strip()) )
				else:
					
					if term in BooleanQuery.OPERATORS.keys():
							next_term = query.pop()
							if "not" in next_term:
								# drug or schizophrenia not treatment exception => schizophrenia not treatment regex 
								#if len(next_term.split("not")) > 1 :
			
								compliment.update(
										self.InvertedIndexObject.get_posting(next_term[4:].strip())
									 )
								continue
							else:
								result = BooleanQuery.OPERATORS[term](result,
										self.InvertedIndexObject.get_posting(next_term) 
									)
					else:
						result.update( self.InvertedIndexObject.get_posting(term) )
				

		except IndexError:
			pass
				

		if compliment !=  set():
			result = self.OPERATORS["not"](result,compliment)
			compliment.clear()	
		
		print(result)
		print([ self.InvertedIndexObject.index[x] for x in result ])
	
	
class InvertedIndex:
	
	def __init__(self, dir ="documents"):
		self.dir = dir
		self.inverted_index = defaultdict(dict)
		self.index = dict()		
		self.build()
		

	def get_posting(self,term):
		if self.inverted_index.__contains__(term):
			return self.inverted_index[term]['posting']
		

	def get_frequency(self,term):
		if self.inverted_index.__contains__(term):
			return self.inverted_index[term]['frequency']

	def build(self):
		count =0
		try:
			for doc_id,document in enumerate( os.listdir(self.dir) ):
				self.index[doc_id] = document
				with open( str(self.dir + os.path.sep + document), 'r') as f:
					for line in f:
						count += 1 
						print(count, end="\r")
						for term in word_tokenize(line.rstrip("\n")):
							try:
								if not self.inverted_index.__contains__(term):
									raise NameError
								self.inverted_index[term]['frequency'] += 1
								self.inverted_index[term]['posting'].add(doc_id)

							except NameError:
								self.inverted_index[term] = {'frequency': 1, 'posting': set([doc_id])}
		except:
			print(count, end="\r")




def main():
	pr = cProfile.Profile()
	pr.enable()
	
	index = InvertedIndex()
	boolean_query = BooleanQuery(index)
	#pprint.pprint(index.inverted_index,indent = 4)
	
	while True:
		try:
			query = input("Enter Query :: ").strip()
		
			boolean_query.search(query)
		except KeyboardInterrupt:
			break
		
	pr.disable()
	s = io.StringIO()
	sortby = 'cumulative'
	ps = pstats.Stats(pr, stream = s).sort_stats(sortby)
	ps.print_stats()
	print(s.getvalue())		



if __name__ == '__main__':
	main()
