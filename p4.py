# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = None
eeprom = ES2EEPROMUtils.ES2EEPROM()
value = 0
pwmLED = None
num_guesses = 0

# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game, value
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        end_of_game = False
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    print(raw_data)
    for i in range(0,12,4): #loop until 12 because we only want 3 blocks 
        print(str(i//4 + 1) + ' - ' + raw_data[i] + raw_data[i + 1] + raw_data[i + 2] + ' took ' + str(raw_data[i + 3]) + ' guesses')
    pass


# Setup Pins
def setup():
    global pwmLED, buzzer
    # Setup board mode

    GPIO.setmode(GPIO.BOARD)
    
    # Setup regular GPIO

    for i in LED_value:
        GPIO.setup(i, GPIO.OUT)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup PWM channels

    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(33, GPIO.OUT)
    pwmLED = GPIO.PWM(LED_accuracy, 100)
    buzzer = GPIO.PWM(33, 1) #set initial frequency to 1 Hz

    # Setup debouncing and callbacks

    GPIO.add_event_detect(18, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=200)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=200)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    score_count = eeprom.read_byte(0)
    # Get the scores
    scores = eeprom.read_block(1, score_count*4)
    # convert the codes back to ascii
    for i in range(len(scores)):
        # only convert first 3 bytes in a block
        if (not (i + 1) % 4 == 0):
            scores[i] = chr(scores[i])
    # return back the results
    return score_count, scores

# Save high scores
def save_scores(name):
    # fetch scores
    s_count, ss = fetch_scores()
    # include new score
    new_score = [name, num_guesses]
    scores = []
    scores.append(new_score)
    # sort
    # Iterate through 1D array and transfrom into 2D array with form [[name, num_guesses],...] so we can use the sort function
    for i in range(0,len(ss),4):
        score = [ss[i] + ss[i + 1] + ss[i + 2], ss[i + 3]]
        scores.append(score)
    # sort based on num_guesses
    scores.sort(key=lambda x: x[1])
    # update total amount of scores
    s_count += 1
    eeprom.write_block(0,[s_count])
    # write new scores
    data = []
    for score in scores:
        for letter in score[0]:
            data.append(ord(letter))
        data.append(score[1])
    eeprom.write_block(1,data)
    pass

# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)

# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess

    # Only enable button presses when game is still being played
    if (not end_of_game):
        # increment led value by 1
        value = bin(get_led_value() + 1)
        #handle overflow
        if (int(value,2) >= 8):
            value = '0b000'
        # chop the '0b' off
        value = value[2:]
        padding = len(LED_value) - len(value)
        for i in range(len(LED_value)):
            channel = LED_value[i]
            if (i < padding):
                GPIO.output(channel, 0)
            else:
                GPIO.output(channel, int(value[i - padding ],2))   
    pass

def get_led_value():
    value = '0b'
    for pin in LED_value:
        value += str(GPIO.input(pin))
    return int(value,2)

# Guess button
def btn_guess_pressed(channel):
    global end_of_game, value, buzzer, pwmLED, num_guesses
    # only allow guess submission when game is in session
    if (not end_of_game):
        name = ''
        num_guesses += 1
        guess = get_led_value()
        start = time.time()
        while GPIO.input(channel) == GPIO.LOW:
            time.sleep(0.01)
            end = time.time()
            if (end - start > 2):
                end_of_game = True
                return
        if (value != guess):
            buzzer.start(0)
            pwmLED.start(0)
            accuracy_leds(guess)
            trigger_buzzer(guess)
        else:
            buzzer.stop()
            pwmLED.stop()
            name = input("Congratulations! You've completed the number shuffle challenge. You took " + str(num_guesses) + " guesses \nPlease enter your name below to save your score: \n")
            while not len(name) == 3:
                name = input('Your name must be 3 characters in length please re-enter your name: \n')
            save_scores(name)
            os.system('clear')
            time.sleep(0.1)
            end_of_game = True
    pass


# LED Brightness
def accuracy_leds(guess):
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    dc = 0
    if (guess > value):
        dc = (8-guess)/(8-value)*100
    else:
        dc = guess/value * 100
    pwmLED.ChangeDutyCycle(dc)
    pass

# Sound Buzzer
def trigger_buzzer(guess):
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global buzzer
    buzzer.ChangeDutyCycle(50)
    diff = abs(value - guess)
    if (diff == 3):
        buzzer.ChangeFrequency(1)
    elif (diff == 2):
        buzzer.ChangeFrequency(2)
    elif (diff == 1):
        buzzer.ChangeFrequency(4)
    else:
        buzzer.ChangeDutyCycle(0) # case where is is not close enough 
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        pwmLED.stop()
        GPIO.cleanup()
