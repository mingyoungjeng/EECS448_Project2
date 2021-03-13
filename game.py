import pygame
import sys
import pygame.freetype
from pygame.sprite import RenderUpdates
from pygame.sprite import Sprite
from board import *

from button import *
from aux import *


from menu import Menu
from button import Button


pygame.freetype.init()

BLUE = (106, 159, 181)
DARKBLUE = (0, 0, 55)
RED = (255, 50, 50)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BTNHEIGHT = 50
BTNWIDTH = 100
BOARD_POS = {
	"board1": (50, 50),
	"board2": (900, 50)
}
MAX_SHIPS = 6

WINDOWWIDTH = 800
WINDOWHEIGHT = 600

bannedPositions = []
allowedLengths = list(range(0, MAX_SHIPS+1))


class Game:
	def __init__(self, width, height):
		pygame.init()
		self.width = width
		self.height = height
		#self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT)) #(850, 850)
		self.screen = pygame.display.set_mode((1670, 850)) #(800, 600)
		self.screen.fill((128,128,128)) # Background color
		self.clock = pygame.time.Clock()
		self.currentMenu = None # Use this to switch between menus
		self.gameState = {
			"state": "start",
			"turn": "n/a"
		}
		self.difficulty = 0

		# Might not keep these.
		self.board1 = Board(self.screen, BOARD_POS["board1"])
		self.board2 = Board(self.screen, BOARD_POS["board2"])
		self.boards = {
			"board1": self.board1,
			"board2": self.board2
		}

		# Set icon and app window title
		pygame.display.set_caption("Battleship")
		pygame.display.set_icon(pygame.image.load("Assets/icon.png"))

		# Options
		self.mute = False


	def gameLoop(self):
		while True:
			for event in pygame.event.get():
				if self.currentMenu != None:
					pass
					#self.currentMenu.update(game.screen)
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				for button in self.currentMenu.buttons:
					button.checkEvent(event)

			self.currentMenu.draw(self.screen)
			pygame.display.flip()
			self.clock.tick(60)

		# Dunno where to put this
		if (gameState.state == "something"):
			# Execute a function
			pass


	# This functions get triggered by gameLoop depending on gameState
	def start():
		# Dunno if this will be useful, but templating.

		# self.screen = p.display.set_mode(size = (850,850))
		# self.createCleanPlate() # Replaced with Board.drawBoard()
		# p.display.flip()

		# Prompt for number of ships
		# This is from their code
		ships = input("Input number of ships to place:")
		while ships not in "123456":
			print("Wrong number! It should be 1, 2, 3, 4, 5, or 6")
			ships = input("Input number of ships to place:")
		return ships

	def setup(self):
		# Implement drag and drop to place ships
		self.board1.addShips(3, (6,6), "vertical")
		self.board1.showShips()

	# Maybe add allowed squares and allowed lengths or something
	def placeShips(self): # might move this into board.py
		# Mouse click on square = origin of ship
		brd = "none"
		while (brd == "none"):
			pos, brd = coords_to_pos(getMouse())

		# Hover - tries potential ships
		running = True
		while running:
			self.boards[brd].drawBoard() # Clears the screen of any previous hovers

			x = pygame.mouse.get_pos()[0]
			y = pygame.mouse.get_pos()[1]

			hover, hover_board = coords_to_pos((x,y))
			length, position, orientation = self.isValidShip(pos, brd, hover, hover_board)

			if length:
				#print(length, position, orientation)
				# Draw transparent ship, make it go away when position changes
				self.boards[brd].addShips(length, position, orientation, True)
			pygame.display.flip()

			# Click - click valid, add ship. Click invalid, do nothing
			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if length:
						self.boards[brd].addShips(length, position, orientation, False)
						self.boards[brd].showShips()

						allowedLengths.remove(length)
						for i in range(0,length):
							pos = (position[0]+i, position[1]) if orientation == "horizontal" else (position[0], position[1]+i)
							bannedPositions.append(pos)

					running = False # Exits the loop

		# Some game logic stuff might go here

	# I am quarantining this ugly code				
	def isValidShip(self, pos, brd, hover, hover_board):
		# Add exception later to where you can only place on the correct board
		if (brd == hover_board): # Can't go off board
			# Horizontal Placement
			# Extra conditions here shouldn't be needed, but sometimes loop is buggy
			if (pos[1] == hover[1]):
				length = abs(pos[0] - hover[0]) + 1
				# Only one ship of each length and can't exceed max length
				if (length in allowedLengths):
					# Can't overlap other ships
					minX = pos[0] if pos[0] < hover[0] else hover[0]
					for x in range(0, length):
						if (minX+x, pos[1]) in bannedPositions:
							return False, False, False
					return length, (minX, pos[1]), "horizontal"

			# Vertical Placement
			if (pos[0] == hover[0]):
				length = abs(pos[1] - hover[1]) + 1

				# Only one ship of each length and can't exceed max length
				if (length in allowedLengths):
					# Can't overlap other ships
					maxY = pos[1] if pos[1] > hover[1] else hover[1]
					for y in range(0, length):
						if (pos[0], maxY-y) in bannedPositions:
							return False, False, False
					return length, (pos[0], maxY), "vertical"
		return False, False, False


	def guess(self):
		# Guess
		# Check valid
		# Is hit or miss?
		# Update board
		pass

	def gameOver(self):
		# Clear everything
		# Change to victory menu
		pass

def coords_to_pos(coords):
	# Converts to a square on a board. Maybe turn into function.
	if (coords[0] >= BOARD_POS["board1"][0]) and (coords[0] <= BOARD_POS["board1"][0]+750) and (coords[1] >= BOARD_POS["board1"][1]) and (coords[1] <= BOARD_POS["board1"][1]+750):
		brd = "board1"
	elif (coords[0] >= BOARD_POS["board2"][0]) and (coords[0] <= BOARD_POS["board2"][0]+750) and (coords[1] >= BOARD_POS["board2"][1]) and (coords[1] <= BOARD_POS["board2"][1]+750):
		brd = "board2"
	else:
		return (0, 0), "none"

	row = int((coords[0] - BOARD_POS[brd][0]) / 75)
	col = int((750 - coords[1] + BOARD_POS[brd][1]) / 75)

	return (row, col), brd

game = Game(WINDOWWIDTH, WINDOWHEIGHT)

def optionAction():
    game.currentMenu = optionsMenu

def returnAction():
	game.currentMenu = mainMenu

def difficultyAction():
	game.difficulty += 1
	game.difficulty %= 3
	for button in game.currentMenu.buttons:
		if not button.name.find('diff'): # Changes the difficulty text (why need NOT?)
			button.text = difficultyDict[game.difficulty]
			button.renderText()
	# print('difficulty = {}'.format(game.difficulty))

def muteAction():
	game.mute = not game.mute
	print("muted = " + str(game.mute))


difficultyDict = {0: 'easy', 1: 'hard', 2: 'impossible'}

mainMenu = Menu(game = game,
				title = 'Main Menu',
				bgColor = BLUE,
				btnTextArray = ['start', 'options', 'quit'],
				fontSize = 20,
				textColorArray = [WHITE] * 3,
				plainColorArray = [DARKBLUE] * 3,
				highlightedColorArray = [RED] * 3,
				centeredPositionArray = [(400, 300), (400, 400), (400, 500)],
				actionArray = [startAction, optionAction, quitGame])

optionsMenu = Menu(game = game,
				title = 'Options',
				bgColor = BLUE,
				btnTextArray = ['option1', 'diff:' + difficultyDict[game.difficulty], 'Return', 'Mute'],
				fontSize = 20,
				textColorArray = [WHITE] * 4,
				plainColorArray = [DARKBLUE] * 4,
				highlightedColorArray = [RED] * 4,
				centeredPositionArray = [(400, 200), (400, 300), (400, 400), (400, 500)],
				actionArray = [defaultAction, difficultyAction, returnAction, muteAction])



game.currentMenu = mainMenu

game.board1.drawBoard()
game.board2.drawBoard()
pygame.display.flip()
game.placeShips()
#game.setup()

game.gameLoop()
