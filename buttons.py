import pygame

class Button:
    def __init__(self, pos, image:pygame.Surface, hover_image=None):
        self.image = image
        if hover_image is None:
            self.hover_image = self.image
        else:
            self.hover_image = hover_image
        self.current_img = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
    def hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_img = self.hover_image
        else:
            self.current_img = self.image
    
    def click(self, mouse_pos, mouse_click):
        if mouse_click and self.rect.collidepoint(mouse_pos):
            return True
        return False