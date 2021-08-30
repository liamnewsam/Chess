class Piece:  # Parent Class
    def __init__(self, pic, pos, col):  # Each piece gets a picture, a position, and a color (black or white)
        self.pic = pic

        self.pos = pos
        self.col = col
        self.moved = False
        self.possible_moves = []


class Pawn(Piece):  # Pawn Class
    def viable_moves(self, board):
        self.possible_moves = []  # Reset list

        # If there is no piece right in front, then we can go there
        if not board[self.pos[1]+1][self.pos[0]]:  # I don't need to check to see if self.y+1 < 8 because if the pawn had made it to the end, then it would have been promoted
            self.possible_moves.append([(self.pos[0], self.pos[1]+1), 0, False])  # The 0 at the end is the placeholder of SPECIAL MOVES: ex. 'castle', 'promote', 'endante' etc..., the False is for the check placeholder

            # If we have not moved yet, we can move 2 spaces forward
            if not self.moved and not board[self.pos[1]+2][self.pos[0]]:
                self.possible_moves.append([(self.pos[0], self.pos[1] + 2), 'jump', False])

        # Checking the left and right places for pieces of the other color
        for q in (-1, 1):
            if -1 < self.pos[0]+q < 8 and board[self.pos[1]+1][self.pos[0]+q] and board[self.pos[1]+1][self.pos[0]+q][0] != ['b', 'w'][self.col]:  # "-1 < self.x+q < 8" I have to make sure it is in range of the list so it doesn't error
                self.possible_moves.append([(self.pos[0]+q, self.pos[1]+1), 0, False])

            elif -1 < self.pos[0] + q < 8 and not board[self.pos[1]+1][self.pos[0]+q] and board[self.pos[1]][self.pos[0]+q] and board[self.pos[1]][self.pos[0]+q][0] != ['b', 'w'][self.col]: # Passant
                self.possible_moves.append([(self.pos[0]+q, self.pos[1]+1), 'passant', False])

        for move in self.possible_moves:
            if move[0][1] == 7:
                move[1] = 'promote'  # if pawn is at the end, then it will do the special 'promote'


class Rook(Piece):  # Rock Class
    def viable_moves(self, board):
        self.possible_moves = []  # Reset list

        for dire in ((1, 0), (-1, 0), (0, 1), (0, -1)):  # Right, Left, Up, Down
            for dist in range(1,8):  # 'dist' is the distance away from the current rook's position
                if -1 < self.pos[0] + dire[0]*dist < 8 and -1 < self.pos[1] + dire[1]*dist < 8:
                    if not board[self.pos[1] + dire[1]*dist][self.pos[0] + dire[0]*dist]:  # If there is no piece on the tile, then it is a valid move
                        self.possible_moves.append([(self.pos[0]+dire[0]*dist, self.pos[1]+dire[1]*dist), 0, False])
                    else:
                        if board[self.pos[1] + dire[1] * dist][self.pos[0] + dire[0] * dist][0] != ['b', 'w'][self.col]:  # Elif there is a piece on the tile but it is of the other player's color, then it is a valid move
                            self.possible_moves.append([(self.pos[0] + dire[0] * dist, self.pos[1] + dire[1] * dist), 0, False])
                        break  # However, since there is a piece on this pos, we must break since we cannot move past pieces.
                else:
                    break  # If the position goes beyond the board's dimensions, then break


class Night(Piece):  # 'Night' Class (I remove the 'k' in knight because 'k' references the 'king' piece)
    def viable_moves(self, board):
        self.possible_moves = []  # Reset list

        for y in [2, 1, -1, -2]:
            x = 1 if abs(y) == 2 else 2
            if -1 < self.pos[1] + y < 8:
                if -1 < self.pos[0] + x < 8 and (not board[self.pos[1]+y][self.pos[0]+x] or board[self.pos[1]+y][self.pos[0]+x][0] != ['b', 'w'][self.col]):
                    self.possible_moves.append([(self.pos[0]+x, self.pos[1]+y), 0, False])
                if -1 < self.pos[0] - x < 8 and (not board[self.pos[1]+y][self.pos[0]-x] or board[self.pos[1]+y][self.pos[0]-x][0] != ['b', 'w'][self.col]):
                    self.possible_moves.append([(self.pos[0]-x, self.pos[1]+y), 0, False])

class Bishop(Piece):  # Bishop Class
    def viable_moves(self, board):
        self.possible_moves = []  # Reset list

        for ydir in [-1, 1]:  # Down, Up
            for xdir in [-1, 1]:  # Left, Right
                q = 1
                while -1 < self.pos[0] + q*xdir < 8 and -1 < self.pos[1] + q*ydir < 8:  # Check to make sure position is within board dimensions
                    if not board[self.pos[1]+q*ydir][self.pos[0]+q*xdir]:  # If there isn't a piece on the tile, then it is a valid move
                        self.possible_moves.append([(self.pos[0]+q*xdir, self.pos[1]+q*ydir), 0, False])
                    else:
                        if board[self.pos[1]+q*ydir][self.pos[0]+q*xdir][0] != ['b', 'w'][self.col]:  # Else, if the piece is of the opponent's color it is valid
                            self.possible_moves.append([(self.pos[0] + q * xdir, self.pos[1] + q * ydir), 0, False])
                        break
                    q += 1
        pass

class Queen(Piece):  # Queen Class
    def viable_moves(self, board):
        self.possible_moves = []  # Reset list

        # A Queen is a combination of both Rook and Bishop:

        # Bishop:
        for dire in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for dist in range(1,8):
                if -1 < self.pos[0] + dire[0]*dist < 8 and -1 < self.pos[1] + dire[1]*dist < 8:
                    if not board[self.pos[1] + dire[1]*dist][self.pos[0] + dire[0]*dist]:
                        self.possible_moves.append([(self.pos[0]+dire[0]*dist, self.pos[1]+dire[1]*dist), 0, False])
                    else:
                        if board[self.pos[1] + dire[1] * dist][self.pos[0] + dire[0] * dist][0] != ['b', 'w'][self.col]:
                            self.possible_moves.append([(self.pos[0] + dire[0] * dist, self.pos[1] + dire[1] * dist), 0, False])
                        break
                else:
                    break

        # Rook
        for ydir in [-1, 1]:
            for xdir in [-1, 1]:
                q = 1

                while -1 < self.pos[0] + q*xdir < 8 and -1 < self.pos[1] + q*ydir < 8:
                    if not board[self.pos[1]+q*ydir][self.pos[0]+q*xdir]:
                        self.possible_moves.append([(self.pos[0]+q*xdir, self.pos[1]+q*ydir), 0, False])

                    else:
                        if board[self.pos[1]+q*ydir][self.pos[0]+q*xdir][0] != ['b', 'w'][self.col]:
                            self.possible_moves.append([(self.pos[0] + q * xdir, self.pos[1] + q * ydir), 0, False])
                        break

                    q += 1

class King(Piece):
    def __init__(self, pic, pos, col, rooks):
        super().__init__(pic, pos, col)
        self.rooks = rooks  # King has additional attribute, rooks. While creating the pieces, the two rooks of a player are assigned to this attribute. This attribute is used for castling

    def viable_moves(self, board):
        self.possible_moves = []  # Reset list

        # Check the 3-by-3 area around the king
        for y in [1, 0, -1]:
            for x in [1, 0, -1]:
                if -1 < self.pos[0] + x < 8 and -1 < self.pos[1] + y < 8 and (not board[self.pos[1]+y][self.pos[0] + x] or board[self.pos[1] + y][self.pos[0] + x][0] != ['b', 'w'][self.col]):
                    self.possible_moves.append([(self.pos[0]+x, self.pos[1]+y), 0, False])

        # Castling:
        if not self.moved:
            for rook in self.rooks:
                if not rook.moved:
                    min(self.pos[0] + 1, rook.pos[0] + 1)
                    max(self.pos[0], rook.pos[0])

                    for pce_in_between in board[self.pos[1]][min(self.pos[0]+1, rook.pos[0]+1):max(self.pos[0], rook.pos[0])]:  # There can't be any pieces in between the rook and the king
                        if pce_in_between:
                            break
                    else:
                        self.possible_moves.append([(self.pos[0] + (2, -2)[rook.pos[0] == 0], self.pos[1]), 'castle' + ['r', 'l'][rook.pos[0]==0], False])
