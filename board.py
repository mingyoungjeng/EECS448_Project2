from time import sleep
import pygame
import glob
import os

from pygame import event
from auxx import *

pygame.init()





BG_COLOR = (83,209,212)

#Quick helper function for getting board coordinates
def coordToBoard(coord):
	print('coord = ', coord)
	x = coord[0] * (boardSize/10)
	y = boardSize - (coord[1] + 1) * (boardSize/10)
	return((x,y))

class Marker(pygame.sprite.Sprite):
	def __init__(self,png, pos, mark):
		super(Marker,self).__init__()
		self.image = pygame.image.load(png)
		# w, h = self.image.get_size()
		# w *= (boardSize / 750) / 8
		# h *= (boardSize / 750) / 8

		self.w = int(boardSize / 10)
		self.h = int(boardSize / 10)
		# self.image = pygame.transform.scale(self.image, (int(w), int(h)))
		self.image = pygame.transform.smoothscale(self.image, (self.w, self.h))
		self.rect = self.image.get_rect()
		pygame.Surface.set_colorkey(self.image,[0,0,0])
		self.pos = pos
		if type(self.pos[0]) == int:
			self.offset = self.pos
		else:
			self.offset = self.pos[0]

		self.mark = mark
		self.rect.topleft = coordToBoard(self.offset)

	def draw(self, surface):
		surface.blit(self.image, self.rect)

class Ship(pygame.sprite.Sprite):
	def __init__(self,png,pos):
		super(Ship,self).__init__()
		self.image = pygame.image.load(png)
		w, h = self.image.get_size()
		w *= (boardSize / 750) / 8
		h *= (boardSize / 750) / 8
		self.image = pygame.transform.scale(self.image, (int(w), int(h)))

		self.rect = self.image.get_rect()
		self.rect.topleft = coordToBoard(pos[0])
		pygame.Surface.set_colorkey(self.image,[0,0,0])
		self.pos = pos

class Board:
	def __init__(self, screen, pos, boardSize):
		self.screen = screen
		self.boardSize = boardSize
		self.surface = pygame.Surface((self.boardSize, self.boardSize))

		self.markers = pygame.sprite.Group() # Array of hit/miss markers
		self.ships = pygame.sprite.Group() # Array of ship sprites
		self.pos = pos
		self.rect = self.surface.get_rect(topleft = self.pos)

		self.drawShips = True
		self.letters = ["A","B","C","D","E","F","G","H","I","J"]
		self.numbers = ["1","2","3","4","5","6","7","8","9","10"]

		# Retrieve Assets
		self.assetsList = {}
		self.assetNameKeys = ["BS 1","BS 2","BS 3","BS 4","BS 5","BS 6", "BS_V 1","BS_V 2","BS_V 3","BS_V 4","BS_V 5","BS_V 6","hit","miss"]
		dir_path = os.path.dirname(os.path.realpath(__file__))
		assetsFolder = glob.glob(dir_path + "/Assets/" + "*")
		for asset in assetsFolder:
			# print(asset)
			for key in self.assetNameKeys:
				if(asset.find(key) != -1):
					self.assetsList[key] = asset

		self.surface.fill(BG_COLOR) #what is this ah oops -katelyn

	def clearBoard(self):
		self.surface.fill(BG_COLOR)
		self.markers.empty()
		self.ships.empty()

	#Used to draw the initial board
	def drawBoard(self):
		# Gridlines and labels
		for x in range(0,11):
			xPos = (x)*self.boardSize/10
			pygame.draw.line(self.surface, (0,0,0), (xPos,0), (xPos,self.boardSize))

		for y in range(0,11):
			yPos = (y)*self.boardSize/10
			pygame.draw.line(self.surface, (0,0,0), (0,yPos), (self.boardSize,yPos))

		textType = pygame.font.Font('freesansbold.ttf', 20)
		#Drawing the letters on axis
		for letter in self.letters:
			textSurf, textRect = self.text_objects(letter, textType)
			x = ord(letter) - 65
			xpos = x*self.boardSize/10 + self.pos[0] + (self.boardSize*.05)
			textRect.center = (xpos, 25) # Make this flexible
			self.screen.blit(textSurf,textRect)

		#Drawing the numbers on axis
		for number in self.numbers:
			textSurf, textRect = self.text_objects(number, textType)
			x = int(number) - 1
			ypos = self.boardSize + (self.boardSize*.05) - x*self.boardSize/10 - self.boardSize/40
			textRect.center = (self.pos[0]-25, ypos)
			self.screen.blit(textSurf,textRect)

		if self.drawShips:
			self.ships.draw(self.surface)
		self.markers.draw(self.surface)
		self.screen.blit(self.surface, self.pos)

	#Creates a sprite at coordinate to represent hit or miss
	def addShot(self, mark, coord):
		if (mark == "hit"):
			png = self.assetsList["hit"]
		else:
			png = self.assetsList["miss"]
		print(str(mark) + " at " + str(coord))
		self.markers.add(Marker(png, coord, mark))
		self.drawBoard()
		pygame.display.flip()

	def addShips(self, length, positions, orientation, hover, valid):
		asset = "BS_V " if orientation == "vertical" else "BS "
		asset += str(length)
		ship = Ship(self.assetsList[asset], positions)

		if hover:
			# Transparency
			ship.image.set_alpha(100)

			# offset position
			ship.rect[0] += self.pos[0]
			ship.rect[1] += self.pos[1]

			if not valid: # tint
				tint = pygame.Surface(ship.image.get_size()).convert_alpha()
				tint.fill((255, 50, 50))
				ship.image.blit(tint, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

			self.screen.blit(ship.image, ship.rect)
		else:
			self.ships.add(ship)


	# Shows ships on board
	def showShips(self):
		self.drawShips = True
		self.drawBoard()
		pygame.display.flip()

	# Hides ships
	def hideShips(self):
		self.drawShips = False
		bg = pygame.Surface((self.boardSize, self.boardSize))
		bg.fill(BG_COLOR)
		self.ships.clear(self.surface, bg)
		self.drawBoard()
		pygame.display.flip()

	#Used to place text on screen
	def text_objects(self,text,font):
		textSurface = font.render(text,True,(0,0,0))
		return textSurface, textSurface.get_rect()

def getMouse():
	"""
	getMouse
			* @pre: That the window has been clicked on
			* @post: gets and returns proper X and Y values for corresponding
				//row and column
			* @param: None
			* @description: creates game loop and event listener the checks for
				//mousebuttondown then gets mouse x and y position and uses board
				//dimentions to create proper number of rows and columns according
				//to x and y set  and returns proper values for xVal and yVal
	"""
	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				# Checks if the left mouse button is clicked
				if pygame.mouse.get_pressed()[0]:
					# assigns x & y with the current position of the mouse.
					x = pygame.mouse.get_pos()[0]
					y = pygame.mouse.get_pos()[1]

					running = False
					#print((x, y))
					return (x, y)
