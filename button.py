import pygame 

#button class
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		else:
			self.clicked = True
   
		self.highlight = False
		self.action = False
		

	def draw(self, surface):
		#print(self.clicked)
		self.action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			self.highlight = True
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				
				self.action = True
				self.clicked = True
				pygame.time.wait(100)   
				
		else:
			self.highlight = False

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
			

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))
		return self.action