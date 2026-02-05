import pygame

class gfx_effects():
    def __init__(self, after_img_ct=1):
        pygame.init()
        
        self.aftimg_dict = {}
        for i in range(after_img_ct):
            self.aftimg_dict[i] = {'t': pygame.time.get_ticks(), 'list': []}
        
    def clear_after_imgs(self, time_index=-1):
        if time_index == -1:
            for k in self.aftimg_dict:
                self.aftimg_dict[k]['list'] = []
        else:
            self.aftimg_dict[time_index]['list'] = []
    
    #used for sprites that change frames
    def draw_after_img(self, screen, scrollx, frame, pos, flip, img_alpha, img_update, img_ct, time_index=0, hsl_en=False):
        #processing after imgs and pos
        after_img = self.aftimg_dict[time_index]
        if pygame.time.get_ticks() - after_img['t'] > img_update:
            temp_img = frame.copy()
            temp_img.set_alpha(img_alpha)
            if hsl_en:
                temp_img = pygame.transform.hsl(temp_img, -170, 0.3, 0.5)#-160
            after_img['list'].append({'img': temp_img, 'flip': flip, 'pos': pos})
            while len(after_img['list']) > img_ct:
                after_img['list'].pop(0)
            after_img['t'] = pygame.time.get_ticks()
        #drawing
        for img_data in after_img['list']:
            img_data['pos'][0] -= scrollx
            screen.blit(pygame.transform.flip(img_data['img'], img_data['flip'], False), img_data['pos'])
            
    #used for large static images
    def draw_after_img_static(self, screen, scrollx, image, pos, img_update, img_ct, time_index=0):
        #processing after imgs and pos
        after_img = self.aftimg_dict[time_index]
        if pygame.time.get_ticks() - after_img['t'] > img_update:
            after_img['list'].append({'img': image, 'pos': pos})
            if len(after_img['list']) > img_ct:
                after_img['list'].pop(0)
            after_img['t'] = pygame.time.get_ticks()
        #drawing
        for img_data in after_img['list']:
            img_data['pos'][0] -= scrollx
            screen.blit(img_data['img'], img_data['pos'])