from npcFile import npc

class save_pt(npc):
    def __init__(self, x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_dict, current_dialogue_list, level, player_inventory):
        super().__init__(x, y, scale, direction, name, ini_vol, enabled, dialogue_list, plot_index_dict)
        self.plot_index = 0
        self.current_level = level
        self.current_p_inv = player_inventory
        self.is_obj = True
        
    def get_dialogue_index(self, level, player_inventory, current_dialogue_index, plot_index_dict, current_dialogue_list):
        pass
    
    def display_interaction_prompt(self, dialogue_enable, player_rect, screen):
        self.player_collision = self.rect.colliderect(player_rect)
        if self.player_collision and self.name != 'invisible_prompt':
            if not dialogue_enable:
                screen.blit(self.interaction_prompt, (self.rect.x + 32, self.rect.y + 32, 32, 32))