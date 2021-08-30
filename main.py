import pygame, random  # I am not the creator of the modules 'pygame' and 'random'.
# ----------------
import game, networking  # I am the creator of the 'game' and 'networking' modules.


# The 'main' program is the one that is executed. It handles the UI, which includes the window, the buttons, the text,
# the images, etc... It also creates chess games using the 'game' module, and uses data calculated in the 'game' object
# to change the current state of the UI. The 'main' program also uses classes from the 'networking' module to connect the player


# I am NOT the creator of the 'pygame', 'random', 'threading', 'time', and 'socket' modules.
# I am NOT the creator of the chess-piece images. I copied them from "https://www.chess.com/".
# I am NOT the creator of the "Helvetica" font.
# I am NOT the creator of the computer images used on "slide" 1.


# colors:
LIGHT_BLUE = (0, 255, 255)
CHESS_WHITE = (234, 237, 206)
CHESS_GREEN = (121, 154, 85)
CHESS_YELLOW = (246, 246, 69)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# image offset:
piecexoffset = -10
pieceyoffset = -15

def evaluate_click(mouse_pos, board_start_pos, board_size):  # Returns the tile position (x, y) that the mouse is on. Ex (3, 4) if not on tile, returns false
    if board_start_pos[0] < mouse_pos[0] < board_start_pos[0] + board_size and board_start_pos[1] < mouse_pos[1] < board_start_pos[1] + board_size:
        return (int((mouse_pos[0] - board_start_pos[0]) / (board_size / 8)), 7 - int((mouse_pos[1] - board_start_pos[1]) / (board_size / 8)))
    else:
        return False

def draw_board(board, screen, board_start_pos, board_size, selected_tile = False):  # Draws the board
    for row in enumerate(board):
        for tile in enumerate(row[1]):
            tile_start_pos_x = int(board_start_pos[0] + tile[0] * board_size / 8)
            tile_start_pos_y = int(board_start_pos[1] + row[0] * board_size / 8)
            tile_end_distance = int(board_size / 8) + 1
            tile_color = [[CHESS_WHITE, CHESS_GREEN][(row[0] + tile[0]) % 2], CHESS_YELLOW][(tile[0], row[0]) == selected_tile]

            pygame.draw.rect(screen, tile_color, (tile_start_pos_x, tile_start_pos_y, tile_end_distance, tile_end_distance))

            piece = tile[1]  # If there is a piece on the tile, then draw it
            if piece:
                screen.blit(piece.pic, (int(tile_start_pos_x + (piecexoffset * board_size / 1000)), int(tile_start_pos_y + (pieceyoffset * board_size / 1000))))


def font_renderer(textd, fonts, texts, colors):  # Updates the dictionary of text with attributes like size, text, and color
    for text in texts:
        textd[text[0].split()[0] if len(text) == 3 else text[3]] = fonts[text[1]].render(text[0], True, colors[text[2]]), fonts[text[1]].size(text[0])

def update_chess_pieces(imaged, additional_imaged, set, game_size):  # Updates chess images
    for color in enumerate('bw'):
        for pce in enumerate('bknpqr'):
            img = pygame.image.load('images\\pieces\\' + set + '\\' + color[1] + pce[1] + '.png')
            img = pygame.transform.scale(img, (int(img.get_size()[0]*game_size/1000), int(img.get_size()[1]*game_size/1000)))
            imaged[color[1] + pce[1]] = img

            img1 = pygame.transform.scale(img, (img.get_size()[0]*5, img.get_size()[1]*5))
            additional_imaged[color[1] + pce[1] + 'l'] = img1
            img2 = pygame.transform.scale(img, (int(img.get_size()[0]*3/5), int(img.get_size()[1]*3/5)))
            additional_imaged[color[1] + pce[1] + 's'] = img2

def update_promotion_media(promotionm, color):  # Updates the promotion images by making them the correct player color (white or black)
    for media in promotionm:
        if media[0] == 'image':
            media[2] = color + media[2][1:]

def on_button(button_pos, mouse_pos):  # returns whether the mouse's pos is on the button inputted
    if button_pos[0] < mouse_pos[0] < button_pos[0] + button_pos[2]:
        if button_pos[1] < mouse_pos[1] < button_pos[1] + button_pos[3]:
            return True
    return False


def start():  # This is called at the bottom of this script.

    # Initialize pygame:
    pygame.init()
    pygame.display.set_caption('Chess')

    # window size
    windowinfo = pygame.display.Info()
    screen_size = screen_width, screen_height = [min(windowinfo.current_w, windowinfo.current_h) - 75 for x in range(2)]
    screen = pygame.display.set_mode(screen_size)

    clock = pygame.time.Clock()

    game_starting_pos = (int(screen_width / 8), int(screen_width / 8))  # Create dimensions of the chess board
    game_size = int(3 * screen_width / 4)

    # images:
    computer_image = pygame.image.load('images\\computerimage.png')  # The 'computer' image is used on slide 1
    computer_image = pygame.transform.scale(computer_image, (int((2 *computer_image.get_size()[0] / 3) * game_size / 1000), int((2 * computer_image.get_size()[1] / 3) * game_size / 1000)))

    images = {}
    additional_images = {'computer': computer_image}  # In the update_chess_pieces function, larger and smaller sized images of each piece is appended to "additional_images"
    update_chess_pieces(images, additional_images, 'original', game_size)

    # font:
    helveticas = pygame.font.Font('fonts\\Helvetica-Bold.ttf', int(36*screen_width/1000))
    helveticam = pygame.font.Font('fonts\\Helvetica-Bold.ttf', int(58*screen_width/1000))
    helvetical = pygame.font.Font('fonts\\Helvetica-Bold.ttf', int(72*screen_width/1000))

    button_texts = [['Play', 2, 0], ['Settings', 2, 0], ['Exit', 2, 0], ['Back', 2, 0], ['Singleplayer', 1, 0],
                    ['Multiplayer', 1, 0], ['Waiting for Player to Join', 1, 0], ['Player1', 1, 0], ['Player2', 1, 0],
                    ['Forfeit', 0, 1], ['Back', 0, 1, 'Backsmall'], ['Player 1 Wins', 0, 2, 'Player1Win'],
                    ['Player 2 Wins', 0, 3, 'Player2Win'], ['Stalemate', 0, 1], [' ', 0, 1, 'promoter'], [' ', 0, 1, 'promoteb'],
                    [' ', 0, 1, 'promoten'], [' ', 0, 1, 'promoteq'], ['Check', 0, 0], ['Draw', 0, 0, 'Drawtitle'],
                    ['Draw', 0, 1, 'Drawtext'], ['Forfeit', 0, 0], ['Draw Accepted', 0, 0, 'drawaccepted'],
                    ['Draw Denied', 0, 0, 'drawdenied'], ['Accept', 0, 0], ['Deny', 0, 0], ['Win by Forfeit', 0, 2, 'player1forfeitwin'],
                    ['Win by Forfeit', 0, 3, 'player2forfeitwin'], ['Draw Prompted', 0, 0, 'Drawprompted']]

    font_dict = {}
    primary_color = (255, 255, 255)  # These colors can be changes later in the settings, although I have not added this functionality yet
    secondary_color = (200, 200, 200)
    font_renderer(font_dict, [helveticas, helveticam, helvetical], button_texts, [primary_color, secondary_color, GREEN, RED])

    # Buttons:
    button_color = (60, 60, 60)
    button_hover_color = (30, 30, 30)

    # Button Dimensions:
    height_buffer = int(screen_height / 100)
    regular_button_height = int(1/9 * screen_height)
    regular_button_width = int(2/5 * screen_width)
    play_button_start_x, play_button_start_y = int(1 / 2 * screen_width) - int(regular_button_width / 2), int(1/2 * screen_height)
    settings_button_start_x, settings_button_start_y = play_button_start_x, play_button_start_y + regular_button_height + height_buffer
    exit_button_start_x, exit_button_start_y = settings_button_start_x, settings_button_start_y + regular_button_height + height_buffer
    singleplayer_button_start_x, singleplayer_button_start_y = int(screen_width / 4) - int(regular_button_width / 2), int(3 * screen_height / 5)
    forfeit_button_start_x, forfeit_button_start_y, forfeit_button_width, forfeit_button_height = game_starting_pos[0], game_starting_pos[1] + game_size + height_buffer, int(regular_button_width/2), int(regular_button_height/2)
    promotion_buttons_size, promotion_buttons_start_y= int(1/9.5 * screen_height), game_starting_pos[0] - height_buffer - int(1/9.5 * screen_height)
    draw_button_start_x, draw_button_start_y, draw_button_width, draw_button_height = game_starting_pos[0] + game_size - forfeit_button_width, game_starting_pos[1] + game_size + height_buffer, forfeit_button_width, forfeit_button_height
    draw_deny_button_start_x, draw_accept_button_start_x = game_starting_pos[0] + game_size - int(forfeit_button_width*3/2) - int(height_buffer / 2), game_starting_pos[0] + game_size - int(forfeit_button_width/2) + int(height_buffer / 2)

    # Promotion media is shown when the player is promoting:
    promotion_media = [['button', [int(screen_width / 2) - int(height_buffer*3/2) - promotion_buttons_size*2, promotion_buttons_start_y, promotion_buttons_size, promotion_buttons_size], ['promoter', [0, 0]]],
                         ['button', [int(screen_width / 2) - int(height_buffer/2) - promotion_buttons_size, promotion_buttons_start_y, promotion_buttons_size, promotion_buttons_size], ['promoten', [0, 0]]],
                         ['button', [int(screen_width / 2) + int(height_buffer/2), promotion_buttons_start_y, promotion_buttons_size, promotion_buttons_size], ['promoteb', [0, 0]]],
                         ['button', [int(screen_width / 2) + int(height_buffer*3/2) + promotion_buttons_size, promotion_buttons_start_y, promotion_buttons_size, promotion_buttons_size], ['promoteq', [0, 0]]],
                       ['image', images, 'wr', [int(screen_width / 2) -int(height_buffer*3/2) - int(promotion_buttons_size*3/2), promotion_buttons_start_y + int(promotion_buttons_size / 2)]],
                       ['image', images, 'wn', [int(screen_width / 2) -int(height_buffer/2) - int(promotion_buttons_size/2), promotion_buttons_start_y + int(promotion_buttons_size / 2)]],
                       ['image', images, 'wb', [int(screen_width / 2) + int(height_buffer/2) + int(promotion_buttons_size/2), promotion_buttons_start_y + int(promotion_buttons_size / 2)]],
                       ['image', images, 'wq', [int(screen_width / 2) + int(height_buffer*3/2) + int(promotion_buttons_size*3/2), promotion_buttons_start_y + int(promotion_buttons_size / 2)]]]

    # Check media is shown when the player is in check:
    check_media = [['text', 0, ['Check', [int(screen_width / 2), int(game_starting_pos[1] + game_size + height_buffer * 4)]]],
                   ['text', 0, ['Check', [int(screen_width / 2), game_starting_pos[1] -(height_buffer*4)]]]]

    # Draw_button is shown in Multiplayer match at the beginning:
    draw_button = ['button', [draw_button_start_x, draw_button_start_y, draw_button_width, draw_button_height],
                   ['Drawtitle', [draw_button_start_x + int(draw_button_width / 2), draw_button_start_y + int(draw_button_height / 2)]]]

    # Draw_prompted_text is shown when a player has clicked the draw_button:
    draw_prompted_text = ['text', 0, ['Drawprompted', [draw_button_start_x + int(draw_button_width / 2), draw_button_start_y + int(draw_button_height / 2)]]]

    # Draw_denied is shown if the player who had prompted a draw is denied:
    draw_denied_text = ['text', 0, ['drawdenied', [draw_button_start_x + int(draw_button_width / 2), draw_button_start_y + int(draw_button_height / 2)]]]

    # Shown when a player receives a draw request:
    draw_deny_button = ['button', [draw_deny_button_start_x, draw_button_start_y, draw_button_width, draw_button_height], ['Deny', [draw_deny_button_start_x + int(draw_button_width / 2), draw_button_start_y + int(draw_button_height / 2)]]]
    draw_accept_button = ['button', [draw_accept_button_start_x, draw_button_start_y, draw_button_width, draw_button_height], ['Accept', [draw_accept_button_start_x + int(draw_button_width / 2), draw_button_start_y + int(draw_button_height / 2)]]]

    slide0_media = [['button', [play_button_start_x, play_button_start_y, regular_button_width, regular_button_height], ['Play', [play_button_start_x + int(regular_button_width / 2), play_button_start_y + int(regular_button_height/2)]]],  # Play Text
                      ['button', [settings_button_start_x, settings_button_start_y, regular_button_width, regular_button_height], ['Settings', [settings_button_start_x + int(regular_button_width / 2), settings_button_start_y + int(regular_button_height/2)]]],
                      ['button', [exit_button_start_x, exit_button_start_y, regular_button_width, regular_button_height], ['Exit', [exit_button_start_x + int(regular_button_width / 2), exit_button_start_y + int(regular_button_height / 2)]]],
                    ['image', additional_images, 'w' + random.choice(['r', 'b', 'n', 'k', 'q', 'p']) + 'l', [int(screen_width / 2), int(screen_height / 4)]]]  # Could we try and make this possibly change every time we visist the home screen? Currently, it stays the same if we visist the home screen again

    slide1_media = [['button', [singleplayer_button_start_x, singleplayer_button_start_y, regular_button_width, regular_button_height], ['Singleplayer', [singleplayer_button_start_x + int(regular_button_width / 2), singleplayer_button_start_y + int(regular_button_height/2)]]],
                      ['button', [singleplayer_button_start_x + int(screen_width/2), singleplayer_button_start_y, regular_button_width, regular_button_height], ['Multiplayer', [singleplayer_button_start_x + int(screen_width /2) + int(regular_button_width/2), singleplayer_button_start_y + int(regular_button_height/2)]]],
                      ['button', [int(screen_width/2)-int(regular_button_width/2), singleplayer_button_start_y + regular_button_height + height_buffer*6, regular_button_width, regular_button_height], ['Back', [int(screen_width/2), singleplayer_button_start_y + regular_button_height + height_buffer*6 + int(regular_button_height/2)]]],
                    ['image', additional_images, 'computer', [int(screen_width / 4), int(2 * screen_height / 5)]],
                    ['image', additional_images, 'computer', [int(screen_width * 5 / 8), int(2 * screen_height / 5)]],
                    ['image', additional_images, 'computer', [int(screen_width * 7 / 8), int(2 * screen_height / 5)]]]

    slide2_media = [['button', [forfeit_button_start_x, forfeit_button_start_y, forfeit_button_width, forfeit_button_height], ['Backsmall', [forfeit_button_start_x + int(forfeit_button_width/2), forfeit_button_start_y + int(forfeit_button_height / 2)]]]]

    slide3_media = [['button', [forfeit_button_start_x, forfeit_button_start_y, forfeit_button_width, forfeit_button_height], ['Backsmall', [forfeit_button_start_x + int(forfeit_button_width/2), forfeit_button_start_y + int(forfeit_button_height / 2)]]]]

    slide4_media = [['text', 0, ['Waiting', [int(screen_width / 2), int(screen_height / 2)]]],
                    ['button', [int(screen_width / 2) - int(forfeit_button_width / 2),singleplayer_button_start_y + forfeit_button_height + height_buffer * 6,forfeit_button_width, forfeit_button_height], ['Backsmall', [int(screen_width / 2),singleplayer_button_start_y + forfeit_button_height + height_buffer * 6 + int(forfeit_button_height / 2)]]],
                    ]

    slide5_media = [['button', [forfeit_button_start_x, forfeit_button_start_y, forfeit_button_width, forfeit_button_height], ['Forfeit', [forfeit_button_start_x + int(forfeit_button_width/2), forfeit_button_start_y + int(forfeit_button_height / 2)]]],
                    draw_button]

    slide6_media = []

    # the "medias" list contains all slide media
    medias = [slide0_media, slide1_media, slide2_media, slide3_media, slide4_media, slide5_media, slide6_media]

    # Background Color:
    background_color = (49, 46, 43)  # Will be able to be changed in settings

    # Additional starting variables:
    slide = 0  # 0 = Menu, 1 = Playing Multiplayer or Singleplayer, 2 = Singleplayer, 3 = Endgame, 4 = Waiting, 5 = Multiplayer, 6 = Settings
    net = False
    draw_prompted = False
    draw_deciding = False
    just_created_game = False
    clicked = False
    promoting = False  # Special case for when we are promoting in game
    player_color = None
    playing = True

    while playing:  # The game loop

        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False  # If a player has clicked the 'x', then we end the loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True  # If a player has clicked the mouse, then we tag it for later consideration

        screen.fill(background_color)  # Draws background

        for media in medias[slide]:  # Only the media found on the current slide gets considered

            if media[0] == 'button':  # Each media can either be 'button', 'image', or 'text'
                current_button_color = button_color  # Each button gets a color different than the background

                if on_button(media[1], pygame.mouse.get_pos()):
                    current_button_color = button_hover_color  # If we are hovering over a button, then that button gets a different color

                    if clicked:  # If it has been clicked, then we will do certain actions depending on the button
                        if media[2][0] == 'Play':
                            slide += 1  # If we clicked play, then we will go on to slide 1

                        elif media[2][0] == 'Settings':
                            pass  # I have not implimented the 'settings' slide yet

                        elif media[2][0] in ['Back', 'Backsmall']:
                            slide = 0  # 'back' brings us back to slide 0
                            if net:
                                net.end()  # If we have a network, then end it
                                if not networking.are_we_host:
                                    net = False

                        elif media[2][0] == 'Exit':
                            playing = False  # Same as clicking the 'x'

                        elif media[2][0] == 'Singleplayer':
                            player_color = random.randint(0, 1)
                            game1 = game.Game(player_color, images)  # If 'singleplayer' button clicked, created a singleplayer game with a random color assigned to the bottom
                            just_created_game = True
                            slide += 1

                        elif media[2][0] == 'Multiplayer':
                            just_created_game = True

                            if not net:
                                net = networking.Host() if networking.are_we_host else networking.Client()
                            slide = 4  # If 'multiplayer' button clicked, we first go to the 'waiting' slide and wait until we have been connected

                        elif 'promote' in media[2][0]:
                            promoting[-1] = media[2][0][-1]  # If a 'promote' button is clicked, then tag the piece we selected

                        elif media[2][0] == 'Forfeit':
                            net.send('forfeit')  # tell the other player we have forfeited
                            game1.endgame = 'fcheckmate0'  # instantly ends the game

                        elif media[2][0] == 'Drawtitle':
                            draw_prompted = True  # 'Drawtitle' is the text on the button, 'Drawtext' is the text shown when a draw is finalized

                        elif media[2][0] == 'Accept':
                            draw_deciding = 'accept'  # Draw accepted

                        elif media[2][0] == 'Deny':
                            draw_deciding = 'deny'  # Draw denied

                    clicked = False  # We need to reset 'clicked' in case it accidentally triggers logic further down

                pygame.draw.rect(screen, current_button_color, media[1]) # Draw the button
                screen.blit(font_dict[media[2][0]][0], (media[2][1][0] - int(font_dict[media[2][0]][1][0] / 2), (media[2][1][1] - int(font_dict[media[2][0]][1][1] / 2))))  # Draw the text

            elif media[0] == 'image':
                image_image = media[1][media[2]]
                screen.blit(image_image, [media[3][0] - int(image_image.get_rect().size[0] / 2), media[3][1] - int(image_image.get_rect().size[1] / 2)])  # Draw the image

            elif media[0] == 'text':
                screen.blit(font_dict[media[2][0]][0], (media[2][1][0] - int(font_dict[media[2][0]][1][0] / 2), (media[2][1][1] - int(font_dict[media[2][0]][1][1] / 2))))  # Draw the texxt

        if slide == 0:  # Menu
            pass  # No additional logic needed for slide 0

        elif slide == 1:  # Playing Multiplayer or Singleplayer?
            pass # No additional logic needed for slide 1

        elif slide == 2 or slide == 5:  # Game (2 == Singleplayer, 5 == Multiplayer

            if just_created_game:  # We need to reset certain things in case we have already played a game
                just_created_game = False

                if promoting:
                    for media in promotion_media:
                        medias[slide].remove(media)  # If the previous game had ended while we were promoted, then we need to now remove the promotion media
                    promoting = False

                if slide == 5:
                    # If we were in the process of draw, reset:
                    slide5_media = [['button', [forfeit_button_start_x, forfeit_button_start_y, forfeit_button_width, forfeit_button_height], ['Forfeit', [forfeit_button_start_x + int(forfeit_button_width / 2), forfeit_button_start_y + int(forfeit_button_height / 2)]]],
                                    draw_button]
                    medias[slide] = slide5_media
                    draw_deciding, draw_prompted = False, False

            if clicked:
                clicked_board = evaluate_click(pygame.mouse.get_pos(), game_starting_pos, game_size)  # returns either tile_position or false

                if clicked_board and not promoting and not draw_deciding: # If we are either promoting or draw_deciding, we cannot interact with chess board
                    valid_move = game1.evaluate_pos(clicked_board)  # game considers clicked tile

                    if valid_move:
                        condition = game1.make_move(*valid_move)  # If the move is valid, then we make the move. 'condition' is ONLY when the move prompts a promotion

                        if condition:
                            promoting = [condition, False]
                            update_promotion_media(promotion_media, condition[-1])

                            for media in promotion_media:
                                medias[slide].append(media)  # Because the move has prompted a promotion, we put up the promotion media

                        else:
                            game1.initiate_next_round() # If we aren't promoting, then we automatically initiate next round

            elif promoting and promoting[-1]:  # If the player has clicked on a promotion button, promoting[-1] had been changed to the piece they decided on
                game1.promote(promoting[0][1], promoting[0][2], promoting[-1])  # promote with the piece the player has decided on
                for media in promotion_media:
                    medias[slide].remove(media)  # remove promotion media
                game1.initiate_next_round()  # initiate next round
                promoting = False

            elif draw_deciding and draw_deciding in ['deny', 'accept']: # if the player has accepted or denied
                net.send('draw.'+draw_deciding)   # notify opponent
                slide5_media.remove(draw_accept_button) # remove 'accept' button
                slide5_media.remove(draw_deny_button)  # remove 'deny' button
                if draw_deciding == 'accept':
                    game1.endgame = 'draw'  # if player has accepted the draw, we immediately end the game
                draw_deciding = False

            if draw_prompted:  # If the 'draw' button has been pressed, update media
                slide5_media.remove(draw_button)
                slide5_media.append(draw_prompted_text)
                draw_prompted = False
                net.send('draw')

            if game1.drawing:
                if game1.drawing == 'denied':  # if the prompted draw has been denied:
                    slide5_media.remove(draw_prompted_text)
                    slide5_media.append(draw_denied_text)
                    game1.drawing = False
                else:  # else, we have been prompted with a draw, so we update the media:
                    slide5_media.remove(draw_button)
                    slide5_media.append(draw_accept_button)
                    slide5_media.append(draw_deny_button)
                    game1.drawing = False
                    draw_deciding = True

            if game1.endgame:  # If the game has ended:

                if net and networking.are_we_host and 'f' not in game1.endgame:
                    net.end()  # End the network

                net = False

                slide = 3  # slide 3 == endgame

                if 'checkmate' in game1.endgame:  # if checkmate has been achieved, put up checkmate media
                    end_text_x, end_text_y = int(screen_width / 2), int(game_starting_pos[0] + [game_size + height_buffer * 4, -(height_buffer * 4)][game1.endgame[-1] == '0'])

                    if game1.endgame[0] == 'f': # if the checkmate was achieved by forfeit, then put up forfeit media
                        end_text = [[font_dict['player' + str((not int(game1.endgame[-1])) + 1) + 'forfeitwin'], [end_text_x, end_text_y]]]

                    else:
                        end_text = [[font_dict['Player' + str((not int(game1.endgame[-1])) + 1) + 'Win'], [end_text_x, end_text_y]]]

                elif game1.endgame == 'stalemate':  # If stalemate has been achieved, put up stalemate media
                    end_text = [[font_dict['Stalemate'], [int(screen_width / 2), int(game_starting_pos[1] + game_size + height_buffer * 4)]],
                                [font_dict['Stalemate'], [int(screen_width / 2), game_starting_pos[1] -(height_buffer*4)]]]

                elif game1.endgame == 'draw':  # If a draw has been achieved, upt up draw media
                    end_text = [[font_dict['Drawtext'], [int(screen_width / 2), int(game_starting_pos[1] + game_size + height_buffer * 4)]],
                                [font_dict['Drawtext'], [int(screen_width / 2), game_starting_pos[1] -(height_buffer*4)]]]

            elif game1.player_in_check in [1, 2]: # elif we are in check, imeediately draw check media
                screen.blit(font_dict[check_media[game1.player_in_check-1][2][0]][0], (check_media[game1.player_in_check-1][2][1][0] - int(font_dict[check_media[game1.player_in_check-1][2][0]][1][0] / 2), (check_media[game1.player_in_check-1][2][1][1] - int(font_dict[check_media[game1.player_in_check-1][2][0]][1][1] / 2))))

            # Draw the board
            draw_board(game1.piece_board[::-1], screen, game_starting_pos, game_size, False if not game1.tile_selected else (game1.tile_selected[0], 7-game1.tile_selected[1]))

        elif slide == 3:  # Endgame

            for text in end_text:  # Blit the end_text we had decided on at the end of the game
                screen.blit(text[0][0], (text[1][0] - int(text[0][1][0]/2), text[1][1] - int(text[0][1][1]/2)))

            draw_board(game1.piece_board[::-1], screen, game_starting_pos, game_size)  # Draw the board

        elif slide == 4:  # Waiting

            if net.connected:  # if we have a connection, create the game
                slide += 1
                if networking.are_we_host:  # if we are the host, then we will create our player's color and send it to the other player so they know what color they are
                    player_color = random.randint(0, 1)  # we are assigned a random color
                    net.send(str(player_color))

                elif not networking.are_we_host:  # if we aren't the host, then we will wait until we have received the opponent's color and then create the game
                    first_message = net.first_message  # This stops the program until it has received a response

                    if 'deny' in first_message:  # this is a special case for when there is already a game taking place; we have been denied so we will leave
                        pass  # I have not implemented this funcionality yet

                    else:
                        player_color = int(not int(first_message))

                game1 = game.Game(player_color, images, net)  # create the game

        clicked = False  # after every iteration of the loop, clicked is reset

        pygame.display.flip()  # a final command required for updating the window

    if net:  # before the program ends, we do one last check to make sure the net has ended
        net.end()

if __name__ == "__main__":  # executes if our name is "main." I don't understand why this approach is used, but I use it anyways
    start()

