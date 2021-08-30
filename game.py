import threading  # I am not the creator of the 'threading' module.
# -------------
import piece  # I am the creator of the 'piece' module

#  This script creates a 'Game' class which deals with the logic of the chess game and also has additional networking
#  functionality.

pieces_dict = {'r': piece.Rook,
                  'n': piece.Night,
                  'b': piece.Bishop,
                  'k': piece.King,
                  'q': piece.Queen}

class Game:
    def __init__(self, player_1_color, images, net=False):
        self.net = False

        if net:  # If this is a multiplayer game, then 'net' will be a networking object
            self.multiplayer = True
            self.net = net

            thread1 = threading.Thread(target=self.listening)  # In the background, the game will be listening to catch any of the oppononent's messages
            thread1.start()
        else:
            self.multiplayer = False

        self.player1color = player_1_color
        self.current_player = [1, 0][player_1_color]
        self.current_player_color = 1

        self.images = images  # Used in the process of initializing pieces

        self.piece_board = [[0 for x in range(8)] for x in range(8)]  # Create a blank board
        self.text_board = [[0 for x in range(8)] for x in range(8)]  # Create a blank board

        self.tile_selected = False  # When the player has selected a tile, then this will be True

        self.player_in_check = False  # 1 == bottome side, 2 == top side, False == None
        self.just_jumped = False  # Becomes true when a pawn has just double-jumped. Used for en passant
        self.drawing = False  # 'draw'ing
        self.endgame = False  # Endgame can either become checkmate, stalemate, forfeit, or draw

        self.create_pieces_and_board()  # Creates the pieces and assigns them to the board
        self.find_all_moves()  # In preparation for round 1

    def create_pieces_and_board(self):  # Used to create pieces and insert them into the piece_board, while also modifying text_board

        for side in (0, 1):
            piece_color = ['b', 'w'][[self.player1color, not self.player1color][side]]

            for pce in enumerate('rnb'):
                # Pieces Board
                self.piece_board[side * 7][pce[0]] = pieces_dict[pce[1]](self.images[piece_color + pce[1]], [[pce[0], 7 - pce[0]][side], 0], [0, 1][piece_color == 'w'])
                self.piece_board[side * 7][7 - pce[0]] = pieces_dict[pce[1]](self.images[piece_color + pce[1]], [[7 - pce[0], pce[0]][side], 0], [0, 1][piece_color == 'w'])

                # Text Board
                self.text_board[side*7][pce[0]] = piece_color + pce[1]
                self.text_board[side*7][7-pce[0]] = piece_color + pce[1]

            # Add the King and Queen:

            # Pieces Board
            self.piece_board[side * 7][[4, 3][self.player1color]] = piece.Queen(self.images[piece_color + 'q'], [[[4, 3], [3, 4]][self.player1color][side], 0], [0, 1][piece_color == 'w'])
            self.piece_board[side * 7][[3, 4][self.player1color]] = piece.King(self.images[piece_color + 'k'], [[[3, 4], [4, 3]][self.player1color][side], 0], [0, 1][piece_color == 'w'], [self.piece_board[side * 7][0], self.piece_board[side * 7][7]])  # We give the king his rooks

            # Text Board
            self.text_board[side*7][[4, 3][self.player1color]] = piece_color + 'q'
            self.text_board[side*7][[3, 4][self.player1color]] = piece_color + 'k'

            # Add the Pawns:
            for x in range(8):
                # Pieces Board:
                self.piece_board[[1, 6][side]][x] = piece.Pawn(self.images[piece_color + 'p'], [[x, 7 - x][side], 1], [0, 1][piece_color == 'w'])
                #Text Board:
                self.text_board[[1, 6][side]][x] = piece_color + 'p'

    def find_all_moves(self):  # Used to find all the moves a certain piece can make
        current_player_color_letter, other_player_color_letter = ['b', 'w'][::[1, -1][self.current_player_color]]
        current_player_oriented_text_board = [self.text_board, [x[::-1] for x in self.text_board[::-1]]][self.current_player]
        can_move = False

        for pce in [x for y in self.piece_board for x in y if x and x.col == self.current_player_color]:  # Find all pieces on the board that are of the current player's color
            pce.viable_moves(current_player_oriented_text_board)
            new_moves_list = []  # We cannot remove things from a list while iterating through it, so we will create new list and assign it to the piece afterwards

            for move in pce.possible_moves:
                hypothetical_board = [x[:] for x in current_player_oriented_text_board[:]]  # We create a copy of the text_board so that we can simulate the move and see if it causes a 'check'

                # Execute move:
                pice = hypothetical_board[pce.pos[1]][pce.pos[0]]
                hypothetical_board[pce.pos[1]][pce.pos[0]] = 0
                hypothetical_board[move[0][1]][move[0][0]] = pice

                if move[1]:  # Special cases: (castling, en passant, and promoting)
                    if 'castle' in move[1]:
                        if not self.player_in_check:
                            hypothetical_board[pce.pos[1]][[0, 7][move[1][-1] == 'r']] = 0  # Place where the rook was is now blank
                            hypothetical_board[move[0][1]][move[0][0] + [1, -1][move[1][-1] == 'r']] = current_player_color_letter + 'r'  # Place next to the king is now where rook is
                        else:
                            continue
                    elif move[1] == 'passant':
                        if self.just_jumped and self.orient_tile_pos(self.just_jumped)[0] == move[0][0] and self.orient_tile_pos(self.just_jumped)[1] == move[0][1]-1:
                            hypothetical_board[move[0][1] - 1][move[0][0]] = 0  # Remove the place underneath the pawn
                        else:
                            continue

                king_indexes = {x[1][0]:(x[0], y[0]) for y in enumerate(hypothetical_board) for x in enumerate(y[1]) if x[1] and x[1][-1] == 'k'}  # Dict comprehension

                if not self.is_check(other_player_color_letter, king_indexes[current_player_color_letter], hypothetical_board): # If we aren't in check, move is valid, now we check if it causes the other player's check
                    new_moves_list.append(move)

                    if move[1] == 'promote':
                        move[2] = {}
                        for pice in [current_player_color_letter + x for x in ('q', 'b', 'n', 'r')]:  # special case 'promote', we need to check for check for each piece promoted
                            hypothetical_board[move[0][1]][move[0][0]] = pice
                            move[2][pice[1]] = self.is_check(current_player_color_letter, [7-x for x in king_indexes[other_player_color_letter]], [x[::-1] for x in hypothetical_board[::-1]])  # We have to reverse the board for other player check
                    else:
                        move[2] = self.is_check(current_player_color_letter, [7-x for x in king_indexes[other_player_color_letter]], [x[::-1] for x in hypothetical_board[::-1]])  # Regular 'check' check

            pce.possible_moves = new_moves_list  # We assign the new_moves_list to the pce's possible_moves attribute

            if pce.possible_moves:
                can_move = True

        if not can_move:
            return 'no possible moves'  # If there are no possible moves, then we have either been stalemated or checkmated

    def is_check(self, other_player_color, king_index, hypothetical_board):  # Algorithm used to determine whether a king is in check
        for xysel in enumerate(((-1, 0), (1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))):  # Check for rook, bishop, and queen positions along with king and pawn posiitons
            x, y = xysel[1]  # x = xdirection (-1, 0, or 1) ; y = ydirection (-1, 0, or 1)
            rook_or_bishop = ['r', 'b'][xysel[0] // 4]  # For the first 4, we check for rook (and queen) and for the last 4 we check for bishop (and queen)
            distance = 1  # Number of tiles away from the king's position in the specified direction
            while -1 < king_index[1] + y*distance < 8 and -1 < king_index[0] + x*distance < 8:
                checking_tile = hypothetical_board[king_index[1] + y*distance][king_index[0] + x*distance]
                if not checking_tile:  # If nothing is on this tile, then continue
                    pass
                elif checking_tile in [other_player_color + x for x in (rook_or_bishop, 'q')]:
                    return True  # If other player's piece on this tile, then player is in check
                elif (distance == 1 and checking_tile in
                      [other_player_color + x for x in ('k', ['k', 'p'][xysel[1] in ((1, 1),(-1, 1))])]):  # Checking squares just around king for other king or pawn
                    return True # Player is in check if king right next to king or if pawns diagonal and up from king
                else:
                    break  # The only other possible case is one of the current player's pieces is on this tile
                distance += 1  # Go one tile further away from the king

        for y in [2, 1, -1, -2]:  # Checking for nights
            xdist = 1 if abs(y) == 2 else 2  # determining the x value based on the specified y value
            for x in [xdist, -xdist]:  # Symmetrically checking the tiles
                if (-1 < king_index[0] + x < 8 and -1 < king_index[1] + y < 8 and
                        hypothetical_board[king_index[1]+y][king_index[0]+x] == other_player_color + 'n'):
                    return True  # If there is the other player's knight on this square, then return True

        return False  # If none of our tests returned True, then the player is NOT in check

    def orient_tile_pos(self, pos):  # Used to orient a tile_pos to match the current player's perspective
        return [(pos[0], pos[1]), (7 - pos[0], 7 - pos[1])][self.current_player]

    def evaluate_pos(self, tile_pos):  # Used to determine whether a player's input is valid

        if self.multiplayer and self.current_player != 0:  # If it is the other player's turn, we can't do anything
            return False

        pce = self.piece_board[tile_pos[1]][tile_pos[0]]  # pce will either be a 0 or a piece object

        if pce and pce.col == self.current_player_color and tile_pos != self.tile_selected:  # If pce is a piece object and the color of the piece object is the current_player's color and this tile isn't selected, then select this tile
            self.tile_selected = tile_pos

        elif self.tile_selected:  # Else, if we have already selected a tile, then consider whether the tile we have selected next is a valid move
            selected_piece = self.piece_board[self.tile_selected[1]][self.tile_selected[0]]

            for move in selected_piece.possible_moves:
                if self.orient_tile_pos(tile_pos) == move[0]:  # if the tile pos is found in any of the possible_move's tile pos, then return True
                    return move, tile_pos  # We are going to make the move

            else:
                self.tile_selected = False  # If it is not a valid move, then just unselect current selected_tile

    def make_move(self, move, tile_pos):  # Once we have determined a move is valid, make the move

        # Execute move on Piece Board:
        pice = self.piece_board[self.tile_selected[1]][self.tile_selected[0]]
        self.piece_board[self.tile_selected[1]][self.tile_selected[0]] = 0
        self.piece_board[tile_pos[1]][tile_pos[0]] = pice

        pice.moved = True  # This attribute is used only in the case of castling, in which both the rook and the king cannot have moved previously
        pice.pos = move[0]  # Update piece's pos

        # Execute move on Text Board
        pce = self.text_board[self.tile_selected[1]][self.tile_selected[0]]
        self.text_board[self.tile_selected[1]][self.tile_selected[0]] = 0
        self.text_board[tile_pos[1]][tile_pos[0]] = pce

        self.just_jumped = False

        if move[2] == 1:  # Update check
            self.player_in_check = [1, 2][not self.current_player]
        else:
            self.player_in_check = False


        if move[1]:  # Special cases:
            if 'castle' in move[1]:
                which_rook = [0, 7][move[1][-1] == ['l', 'r'][self.current_player == 0]]

                pce = self.piece_board[tile_pos[1]][which_rook]
                pce.pos = [move[0][0] + [1, -1][move[1][-1] == 'r'], move[0][1]]  # Update Rook's pos

                self.piece_board[tile_pos[1]][which_rook] = 0
                self.piece_board[tile_pos[1]][tile_pos[0] + [1, -1][bool(which_rook)]] = pce

                pce = self.text_board[tile_pos[1]][which_rook]
                self.text_board[tile_pos[1]][which_rook] = 0
                self.text_board[tile_pos[1]][tile_pos[0] + [1, -1][bool(which_rook)]] = pce
            elif 'passant' in move[1]:
                above_or_below = [-1, 1][self.current_player]
                self.piece_board[tile_pos[1]+above_or_below][tile_pos[0]] = 0
                self.text_board[tile_pos[1]+above_or_below][tile_pos[0]] = 0
            elif 'jump' in move[1]:
                self.just_jumped = tile_pos
            elif 'promote' in move[1]:
                return 'promote', tile_pos, move, ['b', 'w'][self.current_player_color]  # If we are promoting, we must first know what piece the player intends to promote to, then we will promote

        if self.net:  # If we are playing multiplayer, then we will send our move.
            move_we_are_about_to_send = self.format_move(move, self.tile_selected)
            self.net.send(move_we_are_about_to_send)  # THIS IS WHERE WE SEND OUR MOVE

        self.tile_selected = False

    def promote(self, tile_pos, move, piece_selected):  # Special case promote, called once player has decided what piece to promote, finalizes the move process
        self.piece_board[tile_pos[1]][tile_pos[0]] = pieces_dict[piece_selected](self.images[['b', 'w'][self.current_player_color] + piece_selected], move[0], self.current_player_color)
        self.text_board[tile_pos[1]][tile_pos[0]] = ['b', 'w'][self.current_player_color] + piece_selected
        self.player_in_check = [False, [1, 2][not self.current_player]][move[2][piece_selected]]

        if self.net:
            self.net.send(self.format_move(move, self.tile_selected, piece_selected))  # THIS IS WHERE WE SEND OUR MOVE

        self.tile_selected = False

    def format_move(self, move, tile_pos, promotion_piece=False):  # Formatting algorithm that creates a message we send over network
        reg_msg = '.' + ['s', 'c'][move[2] if not promotion_piece else move[2][promotion_piece]] + '.' + str(tile_pos[0]) + str(tile_pos[1]) + '.' + str(move[0][0]) + str(move[0][1])
        if move[1]:
            if move[1] == 'passant':
                msg = 'e' + reg_msg + '.' + str(move[0][0]) + str(move[0][1]-1)
            elif 'castle' in move[1]:
                which_side = move[1][-1] == 'r'
                msg = 'c' + reg_msg + '.' + str([0, 7][which_side]) + '0.' + str(move[0][0] + [1, -1][which_side]) + '0'
            elif move[1] == 'promote':
                msg = promotion_piece + reg_msg
            elif move[1] == 'jump':
                msg = 'j' + reg_msg
        else:
            msg = 'u' + reg_msg

        return msg

    def listening(self):
        while True:
            msg = self.net.receive()  # This stops the thread until a message has been received

            # Messages that do not pertain to moves made in the chess game:
            if msg == 'forfeit':
                self.endgame = 'fcheckmate1'
                break
            elif msg == 'draw':
                self.drawing = True
            elif msg == 'draw.accept':
                self.endgame = 'draw'
                break
            elif msg == 'draw.deny':
                self.drawing = 'denied'
            elif msg == '!DISCONNECT':
                self.endgame = 'fcheckmate1'
                break
            elif msg == 'deny' or msg == None:
                break
            else:
                # Moves that do pertain to moves made in the chess game:
                msgorg = msg.split('.')

                if msgorg[1] == 'c':
                    self.player_in_check = self.current_player
                else:
                    self.player_in_check = False

                self.just_jumped = False  # Don't know if this is good

                pce_start_pos = [7-int(x) for x in msgorg[2]]
                pce_end_pos = [7 - int(x) for x in msgorg[3]]

                pice = self.piece_board[pce_start_pos[1]][pce_start_pos[0]]
                self.piece_board[pce_start_pos[1]][pce_start_pos[0]] = 0
                self.piece_board[pce_end_pos[1]][pce_end_pos[0]] = pice

                pice.moved = True
                pice.pos = [int(x) for x in msgorg[3]]

                pice = self.text_board[pce_start_pos[1]][pce_start_pos[0]]
                self.text_board[pce_start_pos[1]][pce_start_pos[0]] = 0
                self.text_board[pce_end_pos[1]][pce_end_pos[0]] = pice

                if msg[0] == 'c':
                    rook_start_pos, rook_end_pos = [7 - int(x) for x in msgorg[4]], [7 - int(x) for x in msgorg[5]]
                    pice = self.piece_board[rook_start_pos[1]][rook_start_pos[0]]
                    self.piece_board[rook_start_pos[1]][rook_start_pos[0]] = 0
                    self.piece_board[rook_end_pos[1]][rook_end_pos[0]] = pice

                    pice.pos = [int(x) for x in msgorg[5]]

                    pice = self.text_board[rook_start_pos[1]][rook_start_pos[0]]
                    self.text_board[rook_start_pos[1]][rook_start_pos[0]] = 0
                    self.text_board[rook_end_pos[1]][rook_end_pos[0]] = pice
                elif msg[0] == 'e':
                    self.piece_board[pce_end_pos[1]+1][pce_end_pos[0]] = 0
                    self.text_board[pce_end_pos[1] + 1][pce_end_pos[0]] = 0
                elif msg[0] in ['r', 'b', 'n', 'q']:
                    self.piece_board[pce_end_pos[1]][pce_end_pos[0]] = pieces_dict[msg[0]](self.images[['b', 'w'][self.current_player_color] + msg[0]], [int(x) for x in msgorg[2]], self.current_player_color)
                    self.text_board[pce_end_pos[1]][pce_end_pos[0]] = ['b', 'w'][self.current_player_color] + msg[0]
                elif msg[0] == 'j':
                    self.just_jumped = [7-int(x) for x in msgorg[3]]

                self.initiate_next_round()

    def initiate_next_round(self):  # Alternates current_player in preparation for next round
        self.current_player = not self.current_player
        self.current_player_color = not self.current_player_color
        condition = self.find_all_moves()  # Find all moves for the current player
        self.evaluate_condition(condition)  # We check to see if stalemate or checkmate has been achieved

    def evaluate_condition(self, condition):  # We check to see if stalemate or checkmate has been achieved
        if condition:
            if self.player_in_check:
                self.endgame = 'checkmate' + str(int(self.current_player))
            else:
                self.endgame = 'stalemate'
