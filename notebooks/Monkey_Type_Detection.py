#check for long consecutive sequence of consonants
# character_sequence_monkey_type_flag=False
class keyCoordinates():
    def __init__(self,key):
        self.key=key
        self.x=0
        self.y=0
    def set_coordinate(self):
        #assuming - every key is 1X1 units - and the coordinates point to the centroid of a key
        # considering - letter - 'q' -> reference point - at
        #base keys- q, a, z - q-> (0,0),
        line_1=['q','w','e','r','t','y','u','i','o','p','[',']']
        line_2=['a','s','d','f','g','h','j','k','l',';']
        line_3=['z','x','c','v','b','n','m',',','.']
        if self.key in line_1:
            for i in range(len(line_1)):
                #y coordinate is equal, i.e zero - as same as - q, only x is increases
                if self.key==line_1[i]:
                    self.x=i*1
                    self.y=0
        # return x,y
        if self.key in line_2:
            for i in range(len(line_2)):
                #a considered - x=0.5, y=1 -> base - for line 2 keys
                #y coordinate is equal, i.e zero - as same as - q, only x is increases
                if self.key==line_2[i]:
                    self.x=i*1+0.5
                    self.y=1

        if self.key in line_3:
            for i in range(len(line_3)):
                # z considered - x=1, y=2 -> base - for line 3 keys
                #y coordinate is equal, i.e zero - as same as - q, only x is increases
                if self.key==line_3[i]:
                    self.x=i*1+1
                    self.y=2
    def get_coordinates(self,character):
        x,y=self.set_coordinate(character)
        return x,y

    def print_key_coordinates(self):
        print(self.key,": (",self.x,self.y,")")

    @staticmethod
    def get_distance(c1,c2):
        return ((c1.x-c2.x)**2+(c1.y-c2.y)**2)**0.5
    @staticmethod
    def get_actual_length(c1,c2):
        return (c1.x-c2.x),(c1.y-c2.y) #return x, y direction change with magnitude



characters=[
    'q','w','e','r','t','y','u','i','o','p','[',']','a','s','d','f','g','h','j','k','l',';',
    'z','x','c','v','b','n','m',',','.'
]



######### - Monkey type detection methods
import math
import enchant
#now predict the avg msd between the keys in sequence in the address string
#avg euclidean distance b/w any two points in a string is low
text_keyboard_characters=[]
def avg_euclidean_distance(text):
    # for character in text:
    #get coordinates of the character -
    global text_keyboard_characters
    text_keyboard_characters=[keyCoordinates(text[i]) for i in range(len(text))]
    #initialize key coordinates object - with key values
    # print("all keyss....")
    print(text_keyboard_characters[0].key)

    print(text_keyboard_characters[1].key)
    for i in range(len(text)):
        print("i: ",i)
        print("character: ",text_keyboard_characters[i].key)
        text_keyboard_characters[i].set_coordinate() #set coordinates - for a key
        text_keyboard_characters[i].print_key_coordinates()

    #avg distance b/w characters -
    total_length=0
    count=0
    for i in range(len(text_keyboard_characters)):
        for j in range(len(text_keyboard_characters)):
            if i!=j:
                count=count+1
                length=keyCoordinates.get_distance(text_keyboard_characters[i],text_keyboard_characters[j])
                total_length=total_length+length
    avg_msd=total_length/count
    return avg_msd
    # [text_keyboard_characters[i].print_key_coordinates for i in range(len(text_keyboard_characters))]
    # x,y=keyCoordinates.get_coordinates(character)



def detect_msd_monkey_type(text):
    msd_based_monkey_type=False
    avg_msd=avg_euclidean_distance(text)
    if avg_msd<1.5:
        msd_based_monkey_type=True
        print("MSD Based Monkey Typing Detected...")
    return msd_based_monkey_type


def isvowel(character):
    if character in ['a','e','i','o','u']:
        return True
    else: return False

def isconsonant(character):
    if character.isalpha()==True and character not in ['a','e','i','o','u']:
        return True
    else: return False
def is_long_consonant(text):
    # character_sequence_monkey_type_flag=False4
    character_sequence_monkey_type_flag=False
    cc=0
    vc=0
    for character in text:
        if isvowel(character)==True:
            vc=vc+1  #continuos vowel count
            #check if there is a high consecutive consonant length recorded so far-
            cc=0 #if a vowel is encountered - then set the consecutive consonant length

        elif isconsonant(text)==True:
            cc=cc+1
            vc=0 # i.e. if a consonant is encountered - vowel is set to 0

        if cc>3: #high consonant -
            # check if the word is present in english dictionary -
            # American English dictionary
            tag = "en_US"
            # check whether American English(en_US)
            # dictionary exists or not - for the above language
            eng_exist=enchant.dict_exists(tag)
            #check for english
            eng_dict = enchant.Dict(tag)
            if eng_dict.check(text)==False:
                # global character_sequence_monkey_type_flag
                character_sequence_monkey_type_flag=True
                print("Character Sequence Based - Monkey Typing detected...")
                # raise Exception("Monkey Typing Detected... input string not valid...")
                #i.e. if the string is invalid and have high consecutive set of consonants- there is a
                #high risk of being monkey typed
    return character_sequence_monkey_type_flag
# direction_based_monkey_type_flag=False


def recurrent_hand_monkey_typing(text):
    recurrent_hand_monkey_typing_flag=False
    #recurrent pattern of various lengths can occur in a string
    #substring with repetition cannot be >=len(text)/2
    #search for substrings - with length ranging b/w zero to len(text)/2
    for l in range(2,math.ceil(len(text)/2)):
        #substring of length l - is chosen from starting index and
        # frequency of occurence of each possible substring is counted
        for start_index in range(len(text)):
            freq=0
            if start_index+l<len(text):

                substr=text[start_index:start_index+l]
                #look for freq of the above pattern of substr in the text
                freq=text.count(substr)
                if freq>3 and enchant.dict_exists(text)==False:
                    #if the word not found in english dictionary and if the frequency of a particular substring occurs more than
                    #3 times in a string - reccurent pattern based Monkey type identified
                    recurrent_hand_monkey_typing_flag=True
                    print("recurrent based monkey typing detected... with repeated pattern ",substr,"in ",text)
            else: break
    return recurrent_hand_monkey_typing_flag

def direction_change(text):
    direction_based_monkey_type_flag=False
    global text_keyboard_characters
    text_keyboard_characters=[keyCoordinates(text[i]) for i in range(len(text))]
    #initialize key coordinates object - with key values
    # print("all keyss....")
    print(text_keyboard_characters[0].key)

    print(text_keyboard_characters[1].key)
    for i in range(len(text)):
        print("i: ",i)
        print("character: ",text_keyboard_characters[i].key)
        text_keyboard_characters[i].set_coordinate() #set coordinates - for a key
        text_keyboard_characters[i].print_key_coordinates()

    #direction change b/w characters -
    total_length=0
    count=0
    #direction change b/w two consecutive keys - are given be the actual coord diff b/w -
    #k1-k2, k2-k3, and so on for all keys in the text
    i=0
    j=1
    tkc1=text_keyboard_characters[0:-1]
    tkc2=text_keyboard_characters[1:]
    prev_xdiff=0
    prev_ydiff=0
    direction_change=0
    for i,j in zip(tkc1,tkc2):
        #check for direction change and magnitude of change b/w two consecutive keys


        xdiff,ydiff=keyCoordinates.get_actual_length(i,j)
        if (((xdiff>=0)&(prev_xdiff<0)) or ((xdiff<0)&(prev_xdiff>=0))): #direction change - a->b, b->c
            direction_change=direction_change+1
        #we only consider - x coordinate direction here - as the y coordinate - has a maximum - variation of 3 units
        #where y direction change is very likely to happen even in case of monkey typing
        prev_xdiff=xdiff
        prev_ydiff=ydiff
        # total_length=total_length+length
    print("direction change count along x: ", direction_change)
    if direction_change<3:
        print("Risk of Direction based One Hand Monkey typing...\ndirection change count: ",direction_change)
        direction_based_monkey_type_flag=True

    return direction_based_monkey_type_flag

# def get_actual_length():


left_characters=['q','w','e','r','t','a','s','d','f','g','z','x','c','v','b']
right_characters=['y','u','i','o','p','g','h','j','k','l',';','b','n','m',',','.']
#adding g, b - common to both right & left characters

# left_characters=[]
def get_hand(character):
    if character in left_characters:
        return "left"
    elif character in right_characters:
        return "right"
def detect_one_hand_monkey_typing(text):
    """
    baseline preprocessing -
    1. text - lower case
    2. replace all characters except - (a-z)  - with empty character
"""
    #detect the distance between keys typed in sequence
    #check for recurring pattern, msd based, is long consonant, direction based - monkey typing
    recurrent_monkey_hand_typing_flag=recurrent_hand_monkey_typing(text)
    msd_based_monkey_hand_typing_flag=detect_msd_monkey_type(text)
    long_consonant_monkey_hand_typing_flag=is_long_consonant(text)
    direction_based_monkey_typing_flag=direction_change(text)

    #if any of the monkey typing is detected and if word not found in enchant dictionary -
    #monkey typing detected....
    one_hand_monkey_typing_flag=recurrent_monkey_hand_typing_flag or msd_based_monkey_hand_typing_flag or long_consonant_monkey_hand_typing_flag or direction_based_monkey_typing_flag
    if ((one_hand_monkey_typing_flag ==True) and enchant.dict_exists(text)==False):
        print("Monkey Typing detected... and word not found in dictionary...")
        print("Detailed - Monkey Typing Checks : ")
        print("recurrent_hand_monkey_typing: ",recurrent_monkey_hand_typing_flag)
        print("msd_based_monkey_hand_typing_flag: ",msd_based_monkey_hand_typing_flag)
        print("long_consonant_monkey_hand_typing_flag: ",long_consonant_monkey_hand_typing_flag)
        print("direction_based_monkey_typing_flag: ",direction_based_monkey_typing_flag)
    return one_hand_monkey_typing_flag

def two_hand_monkey_typing(text):
    ##
    ##left_characters -
    ##right_characters -
    #separate left and right hand keystroked in a input string in sequence
    left_text=""
    right_text=""
    for character in text:
        if get_hand(character)=='left':
            left_text=left_text+character
        elif get_hand(character)=='right':
            right_text=right_text+character
    #now check for avg_msd, direction_change in left and right text separately -
    print("left text: ",left_text)
    print("right text: ",right_text)
    if left_text!="":
        left_text_monkey_typing=detect_one_hand_monkey_typing(left_text)
    if right_text!="":
        right_text_monkey_typing=detect_one_hand_monkey_typing(right_text)

    if ((left_text_monkey_typing or right_text_monkey_typing) and enchant.dict_exists(text)==False):
        #instead use a location dict
        print("two hand monkey typing detected")
        print("Details on two-hand monkey typing - ")
        print("Left hand monkey typing - ",left_text_monkey_typing)
        print("Right hand monkey typing - ",right_text_monkey_typing)
    else:
        print("no monkey typing detected!!")

#remarks - to check on Two hand monkey typing algorithm
##test

# two_hand_monkey_typing("assdsaddkfjkklm")
#%%
