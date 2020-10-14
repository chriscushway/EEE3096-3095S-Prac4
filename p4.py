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
guess = 0
start = 0
end = 0



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
    global end_of_game
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
    pass


# Setup Pins
def setup():
    randomNumber = generate_number()
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)

    # Setup regular GPIO
    for i in LED_value:
        GPIO.setup(i, GPIO.OUT)

    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print(GPIO.input(btn_submit))
    print(GPIO.input(btn_increase))
    # Setup PWM channels
    # global pwmLED = GPIO.PWM(LED_accuracy, 100)
    # pwmLED.start(0)
    # global pwmBuzz = GPIO.PWM(33, 100)
    # pwmBuzz.start(0)

    # Setup debouncing and callbacks
    GPIO.add_event_detect(18, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=200)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=300)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    # Get the scores
    
    # convert the codes back to ascii
    
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    print('doing an increase')
    value = 0 
    for i in range(len(LED_value)):
        channel = LED_value[len(LED_value) - i - 1]
        value += GPIO.input(channel) * 2**i
    value += 1
    #handle edge case 
    if (value >= 8):
        value = 0
    binary = convertToBinary(value)
    r = 3
    if (len(binary) < 3):
        r= len(binary)
    for i in range(r):
        channel = LED_value[len(LED_value) - i - 1]
        GPIO.output(channel, binary[i]) 
    guess = value
    pass

def convertToBinary(value):
    binary = []
    if (value != 0):
        while value >= 1:
            mod = value % 2

            if (mod > 0):
                binary.append(1)
            else:
                binary.append(0)
            value = value//2
            print(value)
    else:
        binary = [0,0,0]
   
    return binary

# Guess button
def btn_guess_pressed(channel):
    print('doing a guess')
    global end_of_game
    start = time.time()
    while GPIO.input(channel) == GPIO.LOW:
        time.sleep(0.01)
        end = time.time()
        if (end - start > 2):
            end_of_game = True
            return
    
    # start = time.time()
    # while GPIO.input(channel) == GPIO.HIGH:
    #     if (GPIO.input(channel) == GPIO.LOW):
    #         break
    # end = time.time()
    # print(end - start)
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
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
        GPIO.cleanup()
