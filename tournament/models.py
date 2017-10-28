from django.db import models
from league.models import LeagueEvent,Division,LeaguePlayer
import math
import random



# this is still a mess





# Create your models here.
class Tournament(LeagueEvent): #leagueEvent already inherits models.Model, we don have to do it twice
	""" A Tournament is an interface to LeagueEvent, it can 
	"""


	def to_html(self):
		assert (self.number_divisions() == 1)
		division = self.division_set.last()
		return division.bracket.toString()


class TournamentDivision(Division):
	def start(self):
		self.bracket = BracketNode(self.get_players())
	def advance(self): #call this once a week
		self.bracket.advance()
	

class BracketNode(models.Model):
	parent = None
	players = [None,None]
	winner = None
	children = [None,None]
	division = None
	depth = None

	def __init__(self,players,parent = None , depth = 0):
		self.parent = parent
		num_players = len(players)
		if depth == 0:
			num_perfect = 1 << (num_players-1).bit_length()
			players += (num_perfect-num_players)* [None] # find a way to get a better distribution maybe zip?
			num_players = len(players)
		random.shuffle(players)
		print(players)
		if (num_players > 2):
			half = math.floor(len(players) / 2)
			c1 = BracketNode(players[0:half],self,depth+1)
			c2 = BracketNode(players[half:num_players],self,depth+1)
			self.children = [c1,c2]
			self.leaf = False
			self.players = [None,None]
		elif (num_players == 2):
			self.children = [None,None]
			self.leaf = True
			self.players = players
		elif (num_players == 1):
			self.children = [None,None]
			self.players = [players[0], None]
			self.winner = players[0]
			self.leaf = True
		else:
			print ("error in BracketNode.__init__()")


	def get_opponent(self,user):
		if self.players[0] == user:
			return self.players[1]
		if self.players[1] == user:
			return self.players[0]
		if self.leaf:
			return None
		return self.children[0].get_oppenent(user) or self.children[1].get_opponent(user)

	def set_win(self,user):
		if user in self.players:
			self.winner  = user
		elif not self.leaf:
			return self.children[0].set_win(user) or self.children[1].set_win(user)

	def advance(self):
		if (self.players == [None,None]):
			if self.leaf:
				return None
			self.players[0] = self.children[0].advance()
			self.players[1] = self.children[1].advance()
			return None
		elif self.winner != None:
			return self.winner
		else:
			if math.floor(random.random() > 0.5):
				return self.players[0] or self.players[1]
			else:
				return self.players[1] or self.players[0]

	def toString(self,called=True):
		if self.leaf:
			str =  (self.players[0] or "None")  + "\n" + (self.players[1] or "None") + "\n"
			if called:
				return str
			return str,1
		else:
			str1,d1 = self.children[0].toString(False)
			str2,d2 = self.children[1].toString(False)
			d = max(d1,d2)
			str3 = d * "       " + "\\"  + (self.players[0] or "none") + "\n" + d*"       " + "/" + (self.players[1]or "none") + "\n"
			if called:
				return str1+str3+str2
			return str1+str3+str2,d+1


print("\n---------------\n")

x = BracketNode(["1","2","3","4","5","6","7","8", "9","10"])
x.set_win("2")
x.set_win("8")
x.advance()
x.advance()
print(x.toString())

print("\n---------------\n")



