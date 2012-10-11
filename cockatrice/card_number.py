"""
Implemenation of a base 52(?) number system (a (lowercase) to Z (uppercase)) for representing
cards in MtG.
"""
class CardNumber():
	
	def __init__(self, start=0):
		self.index=0
		
	def __convert(self,x):
		v = x		
		if x < 26:
			v += 97
		else:
			v += 39			
		return v
	
	def __str__(self):
	
		h = self.index / (52*52)
		t = (self.index % (52*52)) / 52
		u = self.index % 52 
		h_char = self.__convert(h)	
		t_char = self.__convert(t)	
		u_char = self.__convert(u)			

		return chr(h_char) + chr(t_char) + chr(u_char)
		
	def increment(self):
		self.index += 1