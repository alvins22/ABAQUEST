import pygame
from screeninfo import get_monitors
from abacus import Abacus
import numpy as np
import os
from buttons import Button
import random


def load_and_scale(dir:tuple, sf:tuple, add_scaling:float):
    return_images = ()
    for filename in os.listdir(dir):
        return_images += (pygame.transform.scale_by(pygame.transform.scale_by(pygame.image.load(os.path.join(dir, filename)), sf), add_scaling),)
    return return_images

def scale_images(images:tuple, base_sf:tuple, sfs:tuple):
    return_images = ()
    for i in range(len(images)):
        return_images += (pygame.transform.scale_by(pygame.transform.scale_by(images[i], base_sf), sfs[i]),)
    return return_images

def menu(win, menu_img, text, text_pos, screen_size):
    win.blit(menu_img, (0, 0))
    win.blit(text, text.get_rect(center=(screen_size[0]/2, text_pos[1])))

def map(win, map_img, buttons:Button):
    win.blit(map_img, (0, 0))
    for button in buttons:
        win.blit(button.current_img, button.rect)

def draw_abacus(surface, abacus, width, height, frame_width, rod_width, spacing):
    surface.fill((255, 255, 255))
    x_interval = width/abacus.width - spacing
    bead_height = height/7.5
    bead_pos = np.zeros((7, abacus.width))

    x_pos = frame_width + spacing/2

    for i in range(abacus.width):
        y = frame_width
        pygame.draw.line(surface, (185, 88, 19), (x_pos+x_interval/2, y), (x_pos+x_interval/2, y+height), rod_width)
        for top_interval in range(2):
            if abacus.upper[top_interval, i]:
                pygame.draw.ellipse(surface, (80, 22, 14), (x_pos, y, x_interval, bead_height), 0)
                y += bead_height
                bead_pos[top_interval, i] = y
            else:
                y += bead_height
                bead_pos[top_interval, i] = y
        y += bead_height/2
        for bot_interval in range(5):
            if abacus.lower[bot_interval, i]:
                pygame.draw.ellipse(surface, (80, 22, 14), (x_pos, y, x_interval, bead_height), 0)
                y += bead_height
                bead_pos[bot_interval+2, i] = y
            else:
                y += bead_height
                bead_pos[bot_interval+2, i] = y

        x_pos += x_interval + spacing
    
    pygame.draw.line(surface, (155, 68, 9), (0, bead_height*2 + int(bead_height/4)+frame_width), (width+frame_width*2, bead_height * 2 + int(bead_height/4) + frame_width), int(bead_height/2))
    pygame.draw.rect(surface, (148, 62, 1), (0, 0, width+(frame_width * 2), height+(frame_width * 2)), frame_width)
    return bead_pos, x_interval

def main():
    m = get_monitors()[0]

    user_screen_size = (m.width, m.height)
    # user_screen_size = (1920, 1020)
    desired_size = (1920, 1020)
    scale_factor = (user_screen_size[0]/desired_size[0], user_screen_size[1]/desired_size[1])
    scale = lambda x: (int(x[0]*scale_factor[0]), int(x[1]*scale_factor[1]))
    scale_image = lambda image, sf, add_scaling: (pygame.transform.scale_by(pygame.transform.scale_by(image, sf), add_scaling))

    pygame.init()
    screen = pygame.display.set_mode(user_screen_size)
    pygame.display.set_caption("Abacus Adventure")

    status = "menu"

    clock = pygame.time.Clock()

    # game settings
    answer_feedback_length = 100

    # font set upz
    pygame.font.init()
    title_font = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf", int(300*scale_factor[0]))
    font1 = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf", int(100*scale_factor[0]))
    font2 = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf", int(50*scale_factor[0]))
    font3 = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf", int(90*scale_factor[0]))

    # images load
    image_dir = 'assets/images/'
    map_img_raw = pygame.image.load(image_dir + 'island.jpg')
    map_img = pygame.transform.scale_by(map_img_raw, scale_factor)

    menu_img_raw = pygame.image.load(image_dir + 'beach background.tif')
    menu_img = pygame.transform.scale_by(menu_img_raw, scale_factor)

    abacus_bg_raw = pygame.image.load(image_dir + 'far away view beach.jpg')
    abacus_bg = pygame.transform.scale_by(abacus_bg_raw, scale_factor)

    correct_feedback = load_and_scale("assets/images/feedback/correct", scale_factor, 0.5)
    incorrect_feedback = load_and_scale("assets/images/feedback/incorrect", scale_factor, 0.5)

    check_mark_img_raw = pygame.image.load(image_dir + 'check_mark.png').convert_alpha()
    cross_mark_img_raw = pygame.image.load(image_dir + "cross_mark.png").convert_alpha()

    check_mark = scale_image(check_mark_img_raw, scale_factor, 1)
    cross_mark = scale_image(cross_mark_img_raw, scale_factor, 0.7)


    # abacus set up
    abacus_width = 8
    aba = Abacus(abacus_width)
    width = 960*scale_factor[0]
    height = 500*scale_factor[1]
    frame_width = int(50 * scale_factor[0])
    rod_width = int(30*scale_factor[0])
    spacing = int(6*scale_factor[0])
    abacus_surface = pygame.Surface((width+frame_width*2, height+frame_width*2))

    # read game data
    if os.path.getsize('game data/user_data.txt') == 0:
        select_char = True
        """
        data format:
        00102023020101203021023... : stars for each level
        4 : current level
        0 (boy) 1 (girl) : character the use selected
        """

    else:
        select_char = False

    with open("game data/levels_data.txt", "r") as game_data:
        data = game_data.read().split("\n")
        num_levels = int(data[0])
        level_data = []
        questions = []
        idx = 1
        for i in range(num_levels):
            level_info = data[idx]
            info = tuple(level_info.split(" - "))
            num_questions = int(info[1])
            level_data.append(info)
            questions.append(data[idx+1:idx+num_questions+1])
            idx += num_questions + 1
        if select_char:
            with open("game data/user_data.txt", "w") as user_data:
                user_data.write("0"*num_levels+'\n1\n0')
    
    with open("game data/user_data.txt", "r") as user_data:
        data = user_data.read().split('\n')
        stars = data[0]
        curr_level = int(data[1])
        character = int(data[2])
    

    # buttons setup
    level_button_scale = 0.4
    level_button_raw = pygame.image.load('assets/images/levelButtonOrange.png').convert_alpha()
    level_hover_button_raw = pygame.image.load('assets/images/levelButtonBlue.png').convert_alpha()

    quit_button_img_raw = pygame.image.load('assets/images/quitButton.png')

    start_button_img_raw = pygame.image.load("assets/images/startButton.png")

    submit_button_img_raw = pygame.image.load("assets/images/submitButton.png")
    
    level_button_images = (level_button_raw, level_hover_button_raw, level_button_raw, level_hover_button_raw)
    level_button_scales = (level_button_scale, level_button_scale, level_button_scale*1.12, level_button_scale*1.12)

    return_images = scale_images(level_button_images, scale_factor, level_button_scales)
    level_button, level_hover_button, level4_button, level4_hover_button = return_images


    other_button_images = (quit_button_img_raw, start_button_img_raw, submit_button_img_raw)
    other_button_scales = (0.25, 1, 1)

    other_buttons = scale_images(other_button_images, scale_factor, other_button_scales)

    quit_button_img, start_button_img, submit_button_img = other_buttons


    # button creation
    level_button_pos = ((200, 783), (617, 372), (665, 732), (1160, 330))
    level_button_pos = tuple([(int(i*scale_factor[0]), int(j*scale_factor[1])) for i, j in level_button_pos])
    level_buttons = tuple([Button(level_button_pos[i], level_button, level_hover_button) for i in range(3)])
    level_buttons += (Button(level_button_pos[3], level4_button, level4_hover_button),)

    quit_button = Button(scale((1860, 10)), quit_button_img)
    start_button = Button(scale((860, 800)), start_button_img)
    submit_button = Button(scale((1600, 800)), submit_button_img)

    # abacus answer box
    abacus_answer_box = pygame.Surface((scale((1000, 150))))
    abacus_answer_box.fill((255, 255, 255))

    run = True

    while run:
        mouse_down = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
        
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # if keys[pygame.K_0]:
        #     status = "menu"
        # if keys[pygame.K_1]:
        #     status = "map"
        # if keys[pygame.K_2]:
        #     status = "abacus"
        
        
        if status == "menu":
            text = title_font.render("ABAQUEST", True, (115, 175, 196))
            menu(screen, menu_img, text, scale((500, 300)), user_screen_size)
            screen.blit(start_button.current_img, start_button.rect)
            if start_button.click(mouse_pos, mouse_down):
                if select_char:
                    status = "select char"
                else:
                    status = "map"
        
        elif status == "select char":
            screen.fill((200, 200, 200))
        
        elif status == "map":
            buttons = (level_buttons)
            map(screen, map_img, buttons)
            for i in range(len(level_buttons)):
                level_buttons[i].hover(mouse_pos)
                if level_buttons[i].click(mouse_pos, mouse_down):
                    if i < curr_level:
                        status = "abacus"
                        level_num = i
                        aba.reset()
                        new_level = True

        elif status == "abacus":
            if new_level:
                question_idx = 0
                question_set = questions[level_num]
                random.shuffle(question_set)
                current_level = level_data[level_num]
                questions_in_level = int(current_level[5])
                new_level = False
                select_question = True
                num_right = 0
            
            if select_question:
                curr_question = question_set[question_idx]
                question_data = curr_question.split(' - ')
                question = question_data[0].strip('"')
                if question_data[1] == "numaba":
                    text = "Show the number on abacus:" + question
                    touch_abacus = True
                    abacus_pos_center = (user_screen_size[0]/2, scale((0, 600))[1])
                    show_answer_box = False
                else:
                    text = "What is the number shown on abacus?"
                    touch_abacus = False
                    show_answer_box = True
                    aba.num_to_abacus(question)
                    abacus_pos_center = (user_screen_size[0]/2, scale((0, 450))[1])
                question_text = font1.render(text, True, (255, 255, 255))
                select_question = False
                text = font2.render(f"Question {question_idx+1} / {questions_in_level}", True, (255, 255, 255))
            
            if touch_abacus:
                if mouse_down:
                    if pygame.Rect(abacus_pos_center[0]-width/2, abacus_pos_center[1]-height/2, width, height).collidepoint(mouse_pos):
                        col = (mouse_pos[0] - (abacus_pos_center[0]-width/2))//(x_interval+spacing)
                        col = int(col)
                        for i in range(7):
                            if mouse_pos[1] <= (bead_pos[i, col] + abacus_pos_center[1]-height/2-frame_width):
                                aba.select((i, col))
                                break
            
            screen.blit(abacus_bg, (0, 0))
            bead_pos, x_interval = draw_abacus(abacus_surface, aba, width, height, frame_width, rod_width, spacing)
            screen.blit(abacus_surface, abacus_surface.get_rect(center=abacus_pos_center))
            screen.blit(question_text, question_text.get_rect(center=(user_screen_size[0]/2,scale((0,100))[1])))
            if show_answer_box:
                screen.blit(abacus_answer_box, abacus_answer_box.get_rect(center=(user_screen_size[0]/2,scale((0,850))[1])))

            screen.blit(text, text.get_rect(topright=scale((1840, 0))))

            screen.blit(submit_button.current_img, submit_button.rect)

            if submit_button.click(mouse_pos, mouse_down):
                correct = False
                select_question = True
                frame_num = 0
                if question_data[1] == "numaba":
                    if aba.abacus_to_num() == int(question_data[2]):
                        correct = True
                else:
                    pass
                    
                if correct:
                    status = "right"
                else:
                    status = "wrong"
                question_idx += 1
        
        elif status == "right":
            num_right += 1
            frame_num += 1
            if frame_num == 1:
                screen.fill((255, 255, 255))
                feedback_to_display = random.choice(correct_feedback)
                screen.blit(feedback_to_display, feedback_to_display.get_rect(center=(user_screen_size[0]/2,user_screen_size[1]/2)))
                screen.blit(check_mark, check_mark.get_rect(center=(user_screen_size[0]/2,scale((0, 200))[1])))
            
            if frame_num >= answer_feedback_length:
                status = "abacus"
                if question_idx >= questions_in_level:
                    status = "level ending"
        elif status == "wrong":
            frame_num += 1
            if frame_num == 1:
                screen.fill((255, 255, 255))
                feedback_to_display = random.choice(incorrect_feedback)
                screen.blit(feedback_to_display, feedback_to_display.get_rect(center=(user_screen_size[0]/2,user_screen_size[1]/2)))
                screen.blit(cross_mark, cross_mark.get_rect(center=(user_screen_size[0]/2,scale((0, 200))[1])))
            
            if frame_num >= answer_feedback_length:
                status = "abacus"
                if question_idx >= questions_in_level:
                    status = "level ending"
        
        elif status == "level ending":
            status = "map"
        
        elif status == "practice":
            abacus_pos_center = (user_screen_size[0]/2, scale((0, 500))[1])
            if mouse_down:
                    if pygame.Rect(abacus_pos_center[0]-width/2, abacus_pos_center[1]-height/2, width, height).collidepoint(mouse_pos):
                        col = (mouse_pos[0] - (abacus_pos_center[0]-width/2))//(x_interval+spacing)
                        col = int(col)
                        for i in range(7):
                            if mouse_pos[1] <= (bead_pos[i, col] + abacus_pos_center[1]-height/2-frame_width):
                                aba.select((i, col))
                                break
            
            screen.blit(abacus_bg, (0, 0))
            bead_pos, x_interval = draw_abacus(abacus_surface, aba, width, height, frame_width, rod_width, spacing)
            screen.blit(abacus_surface, abacus_surface.get_rect(center=abacus_pos_center))
            num = str(aba.abacus_to_num())
            num = '0'*(aba.width - len(num)) + num
            num = "      ".join(num)
            text = font3.render(num, True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(user_screen_size[0]/2,scale((0, 150))[1])))

        if keys[pygame.K_a]:
            text = font1.render(str(aba.abacus_to_num()), True, (255, 255, 255))
            screen.blit(text, (10, 10))

        # if keys[pygame.K_b]:
        #     num = input("input num: ")
        #     print("Number: "+num)
        #     aba.num_to_abacus(num)

        if keys[pygame.K_z]:
            status = "practice"

        screen.blit(quit_button.current_img, quit_button.rect)
        if quit_button.click(mouse_pos, mouse_down):
            run = False

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
