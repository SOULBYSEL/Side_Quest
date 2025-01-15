import pygame
import os
import sys

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
background = pygame.image.load(r"C:\\Users\\slend\Downloads\\background.jpg").convert()
#buttons
start_img = pygame.image.load(r"C:\Users\slend\Downloads\Start.png").convert_alpha()
quit_img = pygame.image.load(r"C:\Users\slend\Downloads\Exit.png").convert_alpha()

#button class
class Button():
    def __init__(self, x, y, image, scale):
        b_width = image.get_width()
        b_height = image.get_height()
        self.image = pygame.transform.scale(image, (b_width * scale, b_height * 0.5))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    #draw method
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


start_button = Button(550, 590, start_img, 0.3)
quit_button = Button(850, 600, quit_img, 0.5)

running = True

while running:
    
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if start_button.rect.collidepoint(mouse_pos):
                start_button.clicked = True
            elif quit_button.rect.collidepoint(mouse_pos):
                quit_button.clicked = True

    if start_button.clicked == True:
        # does something
        break
    elif quit_button.clicked == True:
        sys.exit()
        break

    


    screen.blit(background, (0, 0))
    start_button.draw()
    quit_button.draw()
    screen.blit(logo, (640, 200))
    pygame.display.flip()

pygame.quit()