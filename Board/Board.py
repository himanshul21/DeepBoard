import sys
import os
import chess
from Chess_AI.MCTS.MCTS_Main import agent_MCTS
from Chess_AI.MCTS.neural_network_structure import Neural_Network

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button

from Board.Data_Conversion.position_of_mouse import find_position
from Board.Data_Conversion.position_of_pieces import position_dic, conversion_to_number, team_turn
from Board.Data_Conversion.chess_coords_to_real_coords import convert_coordinates
from Board.Data_Conversion.conversion_dictionary import promotion_piece

import random
import time
import re


class Scatter_Text_Widget(Screen):
    
    def __init__(self, **kwargs):
        #Initializes the class with variables
        super(Scatter_Text_Widget, self).__init__(**kwargs)
        
        #Initializes commonly used variables
        self.position = find_position()
        self.position_piece = position_dic
        self.turn = team_turn
        
        #Set the board that is used in the Program
        self.board = chess.Board()
        
    def on_touch_down(self, touch):
        
        #This function gets called when the mouse is pressed, Anywhere on the board
        #Only really generates the data to be used later
        
        res = super(Scatter_Text_Widget, self).on_touch_down(touch)
        #This makes sure the labels keep their Scatter Property and the mouse input can be obtained
        
        if res:
            
            #Gets the chess coord of where the mouse pressed
            pos_chess = self.position.chess_position(touch.pos)
            
            #Saves the data of where, and what was clicked on
            self.clicked_input = [pos_chess,self.position_piece[str(pos_chess)]]

    def on_touch_up(self, touch):
        #This function gets called when the mouse is released
        conversion = convert_coordinates
        scatter = Scatter_Text_Widget()
        self.move_worked = True
        
        res = super(Scatter_Text_Widget, self).on_touch_up(touch)
        
        if res:
            
            #Gets the position of the mouse, and translates it into a chess corrd
            #Saves the variable with self, so the Pawn Promotion can access this data
            self.pos_chess = self.position.chess_position(touch.pos)
            self.chess_position_numerical, self.piece_that_moved = self.get_old_data()

            
            #Checks to see if the user is allowed to move the piece
            if self.turn %2 !=0:
                #The move the user has done
                move = chess.Move.from_uci("%s" %(str(self.chess_position_numerical) + str(self.pos_chess)))
                
                #Checks to see if the move is valid
                is_move_valid = chess.Move.from_uci(str(move)) in self.board.legal_moves
                if is_move_valid == True:
                    #Check for the special move (castle and en passant)
                    is_castling = self.board.is_castling(move)
                    king_side_castling = self.board.is_kingside_castling(move)
ag                    is_en_passant = self.board.is_en_passant(move)
                    
                    #Updates the board
                    #This has to be after checking the special moves
                    self.board.push(move)
                    self.turn += 1
                    
                    #This will capture the piece if the option is available
                    self.check_for_capture()
                    
                    #Executes this code if castling is occuring
                    if is_castling == True:
                        self.castling(king_side_castling, self.pos_chess, conversion)
                        
                    #If the move is en passant then this code is executed
                    if is_en_passant == True:
                        captured_piece_location = str(str(self.pos_chess)[0]) + str(int(str(self.pos_chess)[1]) -1)
                        piece_occupied = str(self.position_piece[captured_piece_location])
                        self.ids[piece_occupied].pos = (1000,1000)
                        
                    #Functionality for every move; moving the piece to the corrent location and updating the dictionary
                    self.every_move_functionality(conversion, self.piece_that_moved)
                
                else:
                    #Check to see if the promotion is occuring
                    not_a_promotion, content, content1, content2, content3 = self.check_for_promotion()
                    
                    if not_a_promotion == True:
                        #If a move is not valid, then move the piece to the starting location
                        self.ids[self.piece_that_moved].pos = (conversion.to_number()[self.chess_position_numerical][0], conversion.to_number()[self.chess_position_numerical][1])
                        self.move_worked = False
                    else:
                        #If a promotion is occuring
                        self.move_worked = False
                        #Add a floatlayout to the popup
                        float = FloatLayout()
                        
                        #Adds the buttons to the layout that were defined based on the color of the promotion piece
                        float.add_widget(content)
                        float.add_widget(content1)
                        float.add_widget(content2)
                        float.add_widget(content3)
                        
                        #Creates the popup, with the FloatLayout as the content, and moves it to a location the user will not see,
                        #so the popup will not be visible, because the popup isn't asthetically pleasing
                        popup = Popup(content=float, size_hint=(None, None), size=(120, 160), auto_dismiss = False, pos_hint={'x':10.0, 'y':10.0})
                        
                        #Binds all of the buttons to the same function, and to close the popup
                        content.bind(on_press = self.promotion, on_release = popup.dismiss)
                        content1.bind(on_press = self.promotion, on_release = popup.dismiss)
                        content2.bind(on_press = self.promotion, on_release = popup.dismiss)
                        content3.bind(on_press = self.promotion, on_release = popup.dismiss)
                        
                        #Opens the popup so the GUI will display it
                        popup.open()
                        
                        #Deletes an array of coordinates
                        del promotion_piece[:]
                        
            else:
                #The player cannot move the black pieces
                self.ids[self.piece_that_moved].pos = (conversion.to_number()[self.chess_positional_numerical][0], conversion.to_number()[self.chess_positional_numerical][1])
                self.move_worked = False
                
        else:
            self.move_worked = False
            
        if self.move_worked == True:
            #This will activate the AI
            self.Agent_move(conversion)
        
    def check_for_promotion(self):
        #Checks to see if a promotion is occuring
        not_a_promotion = True
        pos_piece = '[a-h]8'
        if bool(re.search(str(self.pos_chess), pos_piece)) == True:
            if str(self.piece_that_moved)[6] == 'P':
                if str(self.piece_that_moved)[0] == 'W':
                    if int(self.chess_position_numerical[1]) + 1 == int(str(self.pos_chess)[1]):
                        not_a_promotion = False
                        #If the piece being moved is white
                        #Adds four buttons the user can touch, symbolizing what piece the user wants to promote
                        content = Button(id = "Queen Promotion", background_normal = 'Board\Pictures\White_Queen.png', size = (60,60), pos = (410,300))
                        content1 = Button(id = "Rook Promotion", background_normal = 'Board\Pictures\white_rook.png', size = (60,60), pos = (307.5,400))
                        content2 = Button(id = "Bishop Promotion", background_normal = 'Board\Pictures\white_bishop.png', size = (60,60), pos = (307.5,300))
                        content3 = Button(id = "Knight Promotion", background_normal = 'Board\Pictures\white_knight.png', size = (60,60), pos = (410,400))
                        return not_a_promotion, content, content1, content2, content3
            
        pos_piece = '[a-h]1'
        if bool(re.search(str(self.pos_chess), pos_piece)) == True:
            if str(self.piece_that_moved)[6] == 'P':
                if str(self.piece_that_moved)[0] == 'B':
                    if int(self.chess_position_numerical[1]) + 1 == int(str(self.pos_chess)[1]):
                        not_a_promotion = False
                        #If the piece being moved is white
                        #Adds four buttons the user can touch, symbolizing what piece the user wants to promote
                        content = Button(id = "Queen Promotion", background_normal = 'Board\Pictures\black_Queen.png', size = (60,60), pos = (410,300))
                        content1 = Button(id = "Rook Promotion", background_normal = 'Board\Pictures\black_rook.png', size = (60,60), pos = (307.5,400))
                        content2 = Button(id = "Bishop Promotion", background_normal = 'Board\Pictures\block_bishop.png', size = (60,60), pos = (307.5,300))
                        content3 = Button(id = "Knight Promotion", background_normal = 'Board\Pictures\black_knight.png', size = (60,60), pos = (410,400))
                        return not_a_promotion, content, content1, content2, content3

        return not_a_promotion, "", "", "", ""
    
    def promotion(self, obj):
        conversion = convert_coordinates
        number_conversion = conversion_to_number
        
        #Appends the coordinates to an array
        promotion_piece.append(obj.pos[0])
        promotion_piece.append(obj.pos[1])
        
        #Deletes the pawn
        self.ids[self.piece_that_moved].pos = (10000, 1000)
        
        #Declare what piece was occupied in the location (If the pawn captures to be promoted)
        piece_occupied = str(self.position_piece[self.pos_chess])
        
        #If the square was not empty
        if piece_occupied != None:
            #Delete that piece
            self.ids[piece_occupied].pos = (1000, 1000)
            
        #If the pawn was white
        if self.piece_that_moved[0] == 'W':
            if promotion_piece == [410,300]:
                self.every_move_functionality(conversion, "White Queen")
                self.promotion_number = 5
            elif promotion_piece == [307.5, 400]:
                self.every_move_functionality(conversion, "Left White Rook")
                self.promotion_piece = 4
            elif promotion_piece == [307.5, 300]:
                self.every_move_functionality(conversion, "Left White Bishop")
                self.promotion_piece = 3
            elif promotion_piece == [410, 400]:
                self.every_move_functionality(conversion, "Left White Knight")
                self.promotion_piece = 2
            
        else:
        #If the pawn is BLACK
        #Does the same thing but just changes the ID and the colour of the piece
            if promotion_piece == [410,300]:
                self.every_move_functionality(conversion, "Black Queen")
                self.promotion_number = 5
            elif promotion_piece == [307.5, 400]:
                self.every_move_functionality(conversion, "Left Black Rook")
                self.promotion_piece = 4
            elif promotion_piece == [307.5, 300]:
                self.every_move_functionality(conversion, "Left Black Bishop")
                self.promotion_piece = 3
            elif promotion_piece == [410, 400]:
                self.every_move_functionality(conversion, "Left Black Knight")
                self.promotion_piece = 2
        
        move = chess.Move(number_conversion[str(self.chess_position_numerical)] - 1, number_conversion[str(self.pos_chess)] - 1, promotion = self.promotion_number)
        self.board.push(move)
        self.move_worked = True
        self.turn +=1
        
        
        if self.move_worked == True:
            self.Agent_move(conversion)
    
    def check_for_capture(self):
        try:
            #This will capture a piece if a piece is there to be captured
            piece_occupied = str(self.position_piece[str(self.pos_chess)])
            
            #Deletes the piece that was captured
            self.ids[piece_occupied].pos = (1000,1000)
        except KeyError:
            #If there is nothing to capture, the program will throw a KeyError
            #But we want the program to continue
            pass
    
    def every_move_functionality(self, conversion, piece_that_moved):
        self.ids[piece_that_moved].pos = (conversion.to_number()[self.pos_chess][0], conversion.to_number()[self.pos_chess][1])
        position_dic[str(self.chess_position_numerical)] = None
        position_dic[str(self.pos_chess)] = str(piece_that_moved)
        
        #Move the trail
        self.ids["Trail One"].pos = (conversion.to_number()[self.pos_chess][0], conversion.to_number()[self.pos_chess][1])
        self.ids["Trail Two"].pos = (conversion.to_number()[self.chess_position_numerical][0], conversion.to_number()[self.chess_position_numerical][1])
        
    def castling(self, king_side_castling, pos_chess, conversion):
        #Checks if castling is being initiated, and moves the corrent rook then
        if king_side_castling == True:
            if str(str(pos_chess)[1]) == str(1):
                self.ids['Right White Rook'].pos = (conversion.to_number()['f1'][0], conversion.to_number()['f1'][1])
                position_dic['h1'] = "None"
                position_dic['f1'] = 'Right White Rook'
            else:
                self.ids['Right Black Rook'].pos = (conversion.to_number()['f8'][0], conversion.to_number()['f8'][1])
                position_dic['h8'] = "None"
                position_dic['f8'] = 'Right Black Rook'
        else:
            if str(str(pos_chess)[1]) == str(1):
                self.ids['Left White Rook'].pos = (conversion.to_number()['d1'][0], conversion.to_number()['d1'][1])
                position_dic['a1'] = "None"
                position_dic['d1'] = 'Left White Rook'
            else:
                self.ids['Left Black Rook'].pos = (conversion.to_number()['d8'][0], conversion.to_number()['d8'][1])
                position_dic['a8'] = "None"
                position_dic['d8'] = 'Left Black Rook'
    
    def get_old_data(self):
        piece_that_moved = ""
        index = 8
        
        #Get the old data, and save it
        chess_position_numerical = str(str(str(self.clicked_input)[2]) + str(str(self.clicked_input)[3]))
        while index != len(str(self.clicked_input)) - 2:
            piece_that_moved += str(str(self.clicked_input)[index])
            index += 1
        return chess_position_numerical, piece_that_moved
    
    def Agent_move(self, conversion):
        if self.board.is_game_over(claim_draw = False) == True:
            time.sleep(15)
            os.execv(sys.executable,['python'] + sys.argv)
        #This is where the AI outputs are visualised
        self.board.BLACK = True
        
        ##########################################################
        
        policy_value_net = Neural_Network(training=False)
        
        AI_player = agent_MCTS(policy_value_net.state_score, training = 0)
        
        move, move_probs = AI_player.choose_move(self.board, temperature = 1e-3, probability = 1)
        
        ###########################################################
        
        """
        This will also be needed with the actual algorithm, to 
        visualize the moves
        """
        
        self.board.push(move)
        self.turn +=1
        self.board.BLACK = False
        
        try:
            piece_occupied = str(self.position_piece[str(str(move)[2] + str(move)[3])])
            #Delete the piece that was captured
            self.ids[piece_occupied].pos = (1000, 1000)

        except KeyError:
            pass
        
        #Functionality for every move, moving the piece to the correct location and updating the dictionary
        self.ids[position_dic[str(move)[0] + str(move)[1]]].pos = (conversion.to_number()[str(move)[2] + str(move)[3]][0], conversion.to_number()[str(move)[2] + str(move)[3]][1])       
        
        #The ID of the piece that is being moved
        piece = position_dic[str(move)[0] + str(move)[1]]
        
        position_dic[str(str(move)[0] + str(move)[1])] = "None"
        position_dic[str(str(move)[2] + str(move)[3])] = str(piece)
        
        #Move the trail
        self.ids["Trail One"].pos = (conversion.to_number()[str(move)[2] + str(move)[3]][0], conversion.to_number()[str(move)[2] + str(move)[3]][1]) 
        self.ids["Trail Two"].pos = (conversion.to_number()[str(move)[0] + str(move)[1]][0], conversion.to_number()[str(move)[0] + str(move)[1]][1]) 
        
        
class window(App):
    def build(self):
        return Scatter_Text_Widget()