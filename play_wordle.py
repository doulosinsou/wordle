from nytimesWordlejs import true_fives, guessable
all_words = [*true_fives,*guessable]

from collections import Counter
import statistics
import math
import random
import copy

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class wordle():
    def __init__(self, possible_words: list=true_fives):
        """Instantiate the game with a list of words to play from. Default Wordle potential answers"""
        self.words_to_reduce = possible_words
        self.true_fives = possible_words.copy()
        
        self.game_word = ""
        self.suggestions = []
        self.guesses=[]
        self.guess_count = 0
    
    def set_word(self, word_to_use : str) -> None:
        """For self playing or testing, give the game a word to use."""
        self.game_word = word_to_use
    
    def suggest(self) -> dict:
        """Returns a dictionary with minimum key 'word' to suggest as the next word to guess """
        if len(self.words_to_reduce) <= 2:
            if not self.words_to_reduce:
                return False
            return {'word':self.words_to_reduce[0],'max':1,'min':1,'mean':1}
        
        self.suggestions.append(self.demarcate())
        return self.suggestions[-1]
    
    def guess(self, word: str, manual:bool =False) -> dict:
        """Generates a guess evaluation and returns a dict with boolean key 'won' to mark status of game"""
        word = word.lower()
        response = {'won':False,'code':[],'word':word}
        
        # the manual parameter allows us to manually play by inserting our own code
        if not manual: 
            for i,l in enumerate(word):
                if l==self.game_word[i]:
                    response['code'].append(2)
                elif l in self.game_word:
                    response['code'].append(1)
                else:
                    response['code'].append(0)
        else:
            response['code'] = manual
            
        self.guesses.append(word)
        self.guess_count += 1
        
        if word == self.game_word:
            response['won'] = True
            return response
        
        self.evaluate(response)
        return response
    
    def evaluate(self, guess_response: dict) -> None:
        """Rebuilds words in self.words_to_reduce based on word and code keys in parameter"""
        
        code = guess_response['code']
        guess = guess_response['word']
        for i,c, in enumerate(code):
            letter = guess[i]

            if c == 2:
                #if the letter is in the right position, keep all those words who have this letter in this position
                self.words_to_reduce = [word for word in self.words_to_reduce if word[i]==letter]
            elif c == 1:
                #if the letter is in the word, keep all words who have this letter but NOT in this position
                self.words_to_reduce = [word for word in self.words_to_reduce if (letter in word) and (word[i] is not letter)]
            elif guess.count(letter) < 2:
                #keep remaining words if they do not have this letter
                self.words_to_reduce = [word for word in self.words_to_reduce if (letter not in word)]
        
    
    def demarcate(self) -> dict:
        """
        Generates unique identifiers for every combination of self.true_fives and self.words_to_reduce.
        Returns the word with stats (as a dict) which produces the fewest duplicate identifiers
        """
        
        best_reducer = {"word":"","max":math.inf,"min":math.inf,"mean":math.inf}
        if self.guess_count == 0:
            return {'word': 'raise','max': 167,'min': 1,'mean': 17.49}
        
        #T is the Transformed list, with each row holding all letters in the index position
        T = [l for l in zip(*self.words_to_reduce)]
        for word in self.true_fives:
            score = 0
            for letter, position in zip(word, T):
                #If all letters in position are unique
                if len(set(position)) > 1:
                    #If the letter of potential guess word is one of the unique letters in this postion
                    if letter in position:
                        score+=1
                else:
                    #all letters in position are the same, give this slot a freebee 
                    score+=1
            
            if score < 5:
                #Essentially, every letter must have a valuable contribution in order to pass
                #Words whose letters do not all contribute are now skipped
                continue
            
            #list comprehension to generate an id for each word
            idf = [tuple([0 if word[i] not in check else 2 if word[i] == check[i] else 1 for i in range(5)]) for check in self.words_to_reduce]
            #count how many times word id's occur. The fewer the id count, the better the word is at reducing the guessing pool  
            counted = Counter(idf).values()                     
                                            
            sc_mean = statistics.mean(counted)
            sc_max = max(counted)
            sc_min = min(counted) 
            
            #prepare to compare this word score with the current best
            smaller_max = sc_max < best_reducer["max"]
            eq_max = sc_max == best_reducer["max"]
            smaller_mean = sc_mean < best_reducer["mean"]
            eq_mean = sc_mean == best_reducer["mean"]
            smaller_min = sc_min < best_reducer["min"]
            eq_min = sc_min == best_reducer["min"]

            #sort through the score to determine if it is better than the current best
            if smaller_max or (eq_max and smaller_mean) or (eq_max and eq_mean and smaller_min):
                best_reducer = {"word":word,"max":sc_max,"min":sc_min,"mean":sc_mean, "id":idf}
                
            #if the word generates 100% unique ids, then it is a perfect demarcator, and we don't need to search any further
            if sc_max == 1:
                break
        
        return best_reducer
    
    def self_test(self, word_to_play: str) -> dict:
        """Simulate a round of play, assiging a word from parameter and returning boolean win and number of guesses in a dict"""
        
        self.set_word(word_to_play)
        won = False
        while True:
            s = self.suggest()
            g = self.guess(s['word'])
            
            if g['word'] == self.game_word:
                won = True
                break
            
            if self.guess_count >= 6:
                break
            
            self.evaluate(g)
            
        performance = {
            "won":won,
            "attempts":self.guess_count
        }
        
        return performance
    
    
def suggester(game):
    guesses = [[bcolors.ENDC+u"\u25A1" for i in range(5)] for i in range(6)]
    while True:
        print("*"*40)
        print(f"\n{bcolors.HEADER}This is guess {game.guess_count +1}. Good luck!{bcolors.ENDC}")
        s = game.suggest()

        comment1 = f"""
Try this word: {bcolors.BOLD}{s['word'].upper()}{bcolors.ENDC} 
It will reduce your options to at least {bcolors.OKCYAN}{s['max']}{bcolors.ENDC}
If you wish to use this word, enter 1 . Otherwise please enter the word you chose. 
q: quit \n
"""

        while True:
            input_guess = input(comment1)
            if quit_now(input_guess):break
            if input_guess == '1':
                input_guess = s['word']
                break
            if not_a_char(input_guess): continue
            else: break
        if quit_now(input_guess):break
        comment2 = f"""
Please indicate the wordle response according to this diagram: 
# # # # # \n
0 = gray: letter not in word 
{bcolors.WARNING}1 = yellow{bcolors.ENDC}: letter in word, but not in correct place 
{bcolors.OKGREEN}2 = green{bcolors.ENDC}: letter in word and in correct place \n
"""

        while True:
            input_code = input(comment2).replace(' ','')
            if quit_now(input_code):break
            if not_a_number([0,22222],input_code):continue
            code_list = [int(n) for n in input_code]
            if min(code_list) < 0 or max(code_list) > 2:
                print("Your numbers must be 0, 1, or 2")
                continue 
            lookahead = copy.deepcopy(game)
            lookahead.guess(input_guess, manual=code_list)
            if lookahead.suggest() == False:
                print(f"{bcolors.FAIL}Your numbers do not lead to a valid word, please check them and re-enter {bcolors.ENDC}")
                continue
            break
        if quit_now(input_code):break

        if input_code == "22222":
            print(f"\n{bcolors.OKGREEN}It looks like you won! {bcolors.BOLD}Congratulations!{bcolors.ENDC}")
            break

        game.guess(input_guess, manual=code_list)

        for i,l in enumerate(input_guess):
            if code_list[i] == 0:
                guesses[game.guess_count-1][i] = f"{bcolors.ENDC}{l.upper()}" 
            elif code_list[i] == 1:
                guesses[game.guess_count-1][i] = f"{bcolors.WARNING}{l.upper()}"
            elif code_list[i] == 2:
                guesses[game.guess_count-1][i] = f"{bcolors.OKGREEN}{l.upper()}"

        for count in guesses:
            print(" ".join(count))

def play_the_comp(game):
    random_word = random.choice(game.words_to_reduce)
    game.set_word(random_word)
    guesses = [[bcolors.ENDC+u"\u25A1" for i in range(5)] for i in range(6)]
    while True:
        print("*"*40)
        print(f"\n{bcolors.HEADER}This is guess {game.guess_count +1}. Good luck!{bcolors.ENDC}")
        comment1 = "Guess a five letter word\n"
        while True:
            input_guess = input(comment1)
            if quit_now(input_guess):break
            if not_a_char(input_guess): continue
            if input_guess not in all_words:
                print("This is not a valid guess")
                continue
            g = game.guess(input_guess)
            break
        if quit_now(input_guess):break
        
        for i,l in enumerate(input_guess):
            if l not in game.game_word:
                guesses[game.guess_count-1][i] = f"{bcolors.ENDC}{l.upper()}" 
            elif l in game.game_word and l != game.game_word[i]:
                guesses[game.guess_count-1][i] = f"{bcolors.WARNING}{l.upper()}"
            elif l == game.game_word[i]:
                guesses[game.guess_count-1][i] = f"{bcolors.OKGREEN}{l.upper()}"

        
        for count in guesses:
            print(" ".join(count))


        if g['word'] == game.game_word:
            print(f"\n{bcolors.OKGREEN}You won! {bcolors.BOLD}Congratulations!{bcolors.ENDC}")
            break
        elif game.guess_count == 6:
            print("You're out of guesses! better luck next time!")
            print(f"The word was: {bcolors.OKCYAN}{bcolors.BOLD}{game.game_word}{bcolors.ENDC}")
            break


def not_a_number(valid, test):
    if test.isnumeric() and valid[0] <= int(test) <= valid[1]:
        return False
    else:
        print(f"{bcolors.FAIL}You must enter whole number between {valid[0]} and {valid[1]} {bcolors.ENDC} \n\n")
        return True

def not_a_char(test):
    if test.isalpha() and len(test) == 5:
        return False
    else:
        print(f"{bcolors.FAIL}You must enter a five letter word only. {bcolors.ENDC}\n\n")
        return True

def quit_now(res):
    return True if res.lower() in ['q','quit','exit','done'] else False


if __name__ == "__main__":

    while True:
        game = wordle()

        prompt = """
Would you like to play against the computer, or use the program to help guess Wordle answers? \n
0: play the computer 
1: suggest words for Wordle
q: quit/cancel \n\n
"""
        play_mode = input(prompt)
        if quit_now(play_mode): break  
        if not_a_number([0,1],play_mode): continue
        
        if play_mode == '0':
            play_the_comp(game)
        elif play_mode == '1':
            suggester(game)

        end_prompt = """
Would you like to play again? \n
0: No, I'm done
1: Yes, let's start again!
"""
        while True:
            play_again = input(end_prompt)
            if quit_now(play_again):break
            if not_a_number([0,1],play_again): continue

            if play_again == '0':
                playing = False 
                break 
            if play_again == '1':
                break
        if quit_now(play_again):break

print("Thanks for playing. See you next time.")


    