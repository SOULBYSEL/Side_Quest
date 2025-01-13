import pygame
import os

pygame.init()

os.environ['SDL_VIDEO_CENTERED'] = '1'
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width - 10, screen_height - 50), pygame.RESIZABLE)
pygame.display.set_caption('Side Quest')

#image and colours (loaded before running program)
#logo
logo = pygame.image.load(r"C:\\Users\\slend\Downloads\\logo.png").convert_alpha()
l_width = logo.get_rect().width
l_height = logo.get_rect().height
logo = pygame.transform.scale(logo, (l_width * 0.25, l_height * 0.25))
#background
background = pygame.image.load(r"C:\Users\slend\Downloads\background.jpg").convert()

running = True

while running:
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
    
    screen.blit(background, (0, 0))
    
    screen.blit(logo, (640, 200))
    pygame.display.flip()