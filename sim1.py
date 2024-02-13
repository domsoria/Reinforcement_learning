import numpy as np
import pandas as pd
import time
import sys
from tkinter import *
from PIL import Image, ImageTk
np.random.seed(2)  
w = None
item = None

N_STATES = 5  # the length of the 1 dimensional world
ACTIONS = ['left', 'right']     # available actions
EPSILON = 0.9   # greedy police
ALPHA = 0.1     # learning rate
GAMMA = 0.9    # discount factor
MAX_EPISODES = 10   # maximum episodes
FRESH_TIME = 0.3    # fresh time for one move
passo=140
spazio_passo=50
padding=10
canvas_width = (N_STATES) * (passo + spazio_passo)
canvas_height = 200


class App(object):

    def __init__(self, root):
       self.create_canvas()
        

    def build_q_table(self,n_states, actions):
        table = pd.DataFrame(
            np.zeros((n_states, len(actions))),     # q_table initial values
            columns=actions,    # actions's name
        )
        print(table)    # show table
        return table

    def choose_action(self,state, q_table):
        # This is how to choose an action
        state_actions = q_table.iloc[state, :]
        if (np.random.uniform() > EPSILON) or ((state_actions == 0).all()):  # act non-greedy or state-action have no value
            action_name = np.random.choice(ACTIONS)
        else:   # act greedy
            action_name = state_actions.idxmax()    # replace argmax to idxmax as argmax means a different function in newer version of pandas
        return action_name

    def get_env_feedback(self,S, A):
        # This is how agent will interact with the environment
        if A == 'right':    # move right
            if S == N_STATES - 2:   # terminate
                S_ = 'terminal'
                R = 1
            else:
                S_ = S + 1
                R = 0
        else:   # move left
            R = 0
            if S == 0:
                S_ = S  # reach the wall
            else:
                S_ = S - 1
        #print (S,' ',R,'\r')
        return S_, R

    def update_env(self,S, episode, step_counter):
        env_list = ['-']*(N_STATES-1) + ['T']   # '---------T' our environment
        if S == 'terminal':
            interaction = 'Episode %s: total_steps = %s' % (episode+1, step_counter)
            print('\r{}'.format(interaction), end='')
            time.sleep(2)
            print('\r                                ', end='')
        else:
            env_list[S] = 'o'
            interaction = ''.join(env_list)
            print('\r{}'.format(interaction), end='')
            time.sleep(FRESH_TIME)

    def create_canvas(self):
        self.position=0
        self.pre_position=0
        w = Canvas(root,width=canvas_width,height=canvas_height)
        self.canvas = w
        y = int(canvas_height / 2)
        step=N_STATES+1
        for x in range(step):
            w.create_line(0, y, passo, y, fill="#476042")
            w.create_line((spazio_passo+passo)*x, y, (x+1)*passo+(x*spazio_passo), y, fill="#476042")
        self.create_premio()
        self.create_agent()
        w.pack()
        root.after(2000, self.start_train)

    def create_premio(self):
        two = ImageTk.PhotoImage(file=r'./panino_small.png')
        root.two = two 
        w = self.canvas
        w.create_image((canvas_width-passo,20), image=two, anchor='nw')
    
    def create_agent(self):
        one = ImageTk.PhotoImage(file=r'./dogsmall.png')
        root.one = one  
        w = self.canvas
        item = w.create_image((padding,20), image=one, anchor='nw')
        self.dog=item
    
    def update_canvas(self,S, episode, step_counter):
        step = passo+spazio_passo
        w = self.canvas
        posix=(S)*(passo+spazio_passo)

        if S == 'terminal':
            item = self.dog
            w.move(item,step,0)
            w.update()
            time.sleep(FRESH_TIME*2)
            w.delete(item)
            w.update()
            interaction = 'Episode %s: total_steps = %s' % (episode+1, step_counter)
            print(format(interaction))
            item = self.dog = None

        else:
            item = self.dog
            if (not self.dog):
                #print ("RESET")
                self.pre_position = 0
                self.position = step = 0
                #one = ImageTk.PhotoImage(file=r'./dogsmall.png')
                #item = w.create_image((posix,20), image=one, anchor='nw')
                #self.dog=item
                self.create_agent()
            else:
                self.pre_position = self.position
                self.position=posix
                step=0
                if (self.position > self.pre_position):
                    step = passo+spazio_passo
                elif (self.position < self.pre_position):
                    step = -passo-spazio_passo
            #print(str(S) + "    new position : " + str(step) + " pre_position: " + str(self.pre_position))
            w.move(self.dog,step,0)

        w.update()
        time.sleep(FRESH_TIME)

    def rl(self):
        # main part of RL loop
        q_table = self.build_q_table(N_STATES, ACTIONS)
        for episode in range(MAX_EPISODES):
            step_counter = 0
            S = 0
            is_terminated = False
            #self.update_env(S, episode, step_counter)
            #self.update_canvas(S, episode, step_counter)

            while not is_terminated:

                A = self.choose_action(S, q_table)
                S_, R = self.get_env_feedback(S, A)  # take action & get next state and reward
                q_predict = q_table.loc[S, A]
                if S_ != 'terminal':
                    q_target = R + GAMMA * q_table.iloc[S_, :].max()   # next state is not terminal
                else:
                    q_target = R     # next state is terminal
                    is_terminated = True    # terminate this episode

                q_table.loc[S, A] += ALPHA * (q_target - q_predict)  # update


                S = S_  # move to next state
                self.update_canvas(S, episode, step_counter+1) 

                #self.update_env(S, episode, step_counter+1)
                step_counter += 1
            print(q_table)

        return q_table

    def start_train(self):
        q_table = self.rl()
        print('\r\nQ-table:\n')
        print(q_table)


root = Tk()
app = App(root)
root.mainloop()
root.destroy() # optional;

    
