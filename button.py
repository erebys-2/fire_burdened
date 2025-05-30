import pygame 
from textManager import text_manager #type: ignore

#button class
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale))).convert_alpha()
		self.image2 = pygame.transform.hsl(image, 0, -0.5, -0.2).convert_alpha()
		self.image3 = pygame.transform.hsl(image, 0, -0.5, 0.1).convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		else:
			self.clicked = True
   
		self.highlight = False
		self.action = False
  
		self.text_manager0 = text_manager(0,0,32*scale)
  
		self.highligh_rect = self.rect.scale_by(1.2)
  
		self.count_down = 0
		self.img_highlight_en = True
		self.force_body_highlight = False
		
	def show_text(self, screen, font, text):
		# self.text_manager0.disp_text_box(screen, font, text, (-1,-1,-1), (0,0,0), 
        #                            (self.rect.x + 18, self.rect.y - 8, 32, 64), False, False, 'none')
		if self.highlight:
			color = (200,200,120)
		else:
			color = (200,200,200)
        
		self.text_manager0.disp_text_box(screen, font, text, (-1,-1,-1), color, 
                                   (self.rect.x + 8, self.rect.y - 10, 32, 64), False, False, 'none')
		
	def draw_border(self, surface):
		pygame.draw.rect(surface, (200,200,120), self.rect)
  

	def draw(self, surface):
		#print(self.clicked)
		if self.count_down == 1:
			self.count_down = 0
		self.action = False
  
		
		if self.count_down == 0:
			img = self.image
		else:
			img = self.image2
  
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			self.highlight = self.img_highlight_en
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.action = True
				self.clicked = True
				
			if self.img_highlight_en and self.count_down == 0:
				img = self.image3
		elif self.force_body_highlight:
			img = self.image3
			#self.force_body_highlight = False
		else:
			self.highlight = False


		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
			

		#draw button
		
		surface.blit(img, (self.rect.x, self.rect.y))
		
		if self.action:
			self.count_down = 10
   
		if self.count_down > 0:
			self.count_down -= 1
  
		return self.count_down == 1

	