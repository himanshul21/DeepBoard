'''
It translate the coordinates of the mouse into what position of the chessboard the mouse is in

IF YOU DON'T KNOW THE CHESS POSITIONS: http://www.chess-poster.com/english/learn_chess/notation/images/coordinates_2.gif
'''

from Board.Data_Conversion.conversion_dictionary import dictionary_of_numbers_to_letters as n2l
import math

class find_position():
    def chess_position(self, pos):
        return str(str(n2l[math.ceil(pos[0]/102.5)]) + str(math.ceil(pos[1]/100)))

        

