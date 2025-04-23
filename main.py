# Notes
# gonna try my best to avoid deeply nesting code cause I heard thats bad so bear with me here
#
#
# Libraries and Packages ----------------------------------------------------------------------:

import os  # for clearing the screen
import platform  # for OS compatibilty(cls() is used for windows clear screen while clear() is used for MacOS and Linux)
import random  # for random card choice
from printf import printb # slow print (commit test)
from time import sleep # Cinematic pausing

# Variables -----------------------------------------------------------------------:
small_blind_amount = 5 # default blind amounts
big_blind_amount = 10
dealer_pos = 0 # this player takes the small blind
pot = 0 # the pot(might get removed)
dev = False # this being manually set to true will override certain errors from being raised for testing reasons
folded = []
prev_bet = 0
# Classes -------------------------------------------------------------------------:

class Player:
    def __init__(self,chips):
        self.chips = chips
        self.check = []
        # these are toggleable test hands for forcing edge cases
        # self.hand = [[3,'♢'],[3,'♢'],[3,'♢'],[4,'♢'],[4,'♢'],[4,'♢']] # two three of a kinds
        # self.hand = [[14,'♢'], [2,'♢'], [3,'♢'], [4,'♢'], [5,'♢'], ] # Ace-low straight
        # self.hand = [[14,'♢'], [2,'♢'], [3,'♢'], [4,'♢'], [5,'♢'], [6,'♡']]
        # self.hand = [[2,'♢'], [3,'♢'], [4,'♢'], [7,'♢'], [6,'♡']]
        # self.hand = [[3,'♠'],[2,'♢'],[2,'♡'],[2,'♣'],[2,'♠']]
        # self.hand = [[14,'♢'], [14,'♠'], [9,'♣'], [8,'♢'], [7,'♢'], ]
        self.hand = []
        self.current_bet = 0  # Track the current player's bet in this round
        self.folded = False   # Track if player folded
        self.all_in = False   # Track if player is all-in

    def convertToStr(self):
        card_strings = []
        for card in self.hand:
            value = card[0]
            suit = card[1]

            # Convert numerical value to rank
            if value == 14:
                rank = "A"
            elif value == 13:
                rank = "K"
            elif value == 12:
                rank = "Q"
            elif value == 11:
                rank = "J"
            else:
                rank = str(value)

            card_name = f"{rank}{suit}"
            card_strings.append(card_name)

        return card_strings

    def __str__(self):
        hand_str = ", ".join(str(card) for card in self.convertToStr())
        return f"your hand: {hand_str}\nyour chips: {self.chips}"

# Functions -----------------------------------------------------------------------:

def clear_console(): # command to clear console, used to reduce clutter
    if platform.system() == "Windows":
        os.system("cls")  # Clear console for Windows
    else:
        os.system("clear")  # Clear console for macOS/Linux

def create_deck(): # creates a standard deck of cards
    suits = ['♡', '♢', '♣', '♠'] # suits
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] # ranks
    deck = {} # deck dict to add cards to

    for suit in suits: #embedded for loop to make every card
        for rank in ranks:
            card_name = f"{rank}{suit}" # str syntax for the key
            if rank == 'J': # setting val of face cards
                value = 11
            elif rank == 'Q':
                value = 12
            elif rank == 'K':
                value = 13
            elif rank == 'A':
                value = 14
            else:
                value = int(rank) #everything else is just the int version of the key
            deck[card_name] = [value,suit]  # adds the card to the deck
    return deck # returns the deck

def draw(person): # function to draw a card, parameters for hand so it can be reused for the A
    card_names = list(holdem.keys())  # Get a list of available card names
    cardnum = random.randint(0, len(card_names) - 1) # this sets the range based on how many cards there are to prevent an index error
    drawn_card = list(holdem.keys())[cardnum] # this gets the key
    cardval = holdem.pop(drawn_card) # this gets the value and removes (pops) the item from the deck
    # Add the drawn card to the player's hand
    person.hand.append(cardval)
    return person.hand # Return the updated value

def read(itemToRead): # This is a small function to change 11 12 13 and 14 to their proper card name when using showdown()
    if itemToRead == 11:
        return "jack" # returns the string name of the card instead
    elif itemToRead == 12:
        return "queen"
    elif itemToRead == 13:
        return "king"
    elif itemToRead == 14:
        return "ace"
    else:
        return itemToRead

def showdown(person):
    # these are what i call factor hands, essentially hands that are a part of a different hand. a flush is part of a straight flush, three is part of full house and pair is part of two pair and full house. these are activated when it finds such a hand so it can make "product hands" out of these even if they arent your best
    river = person.hand+table.hand # usable cards for the player
    hasFlush = False # if you have a flush, it checks if its also a straight since there can only be one flush per suit in 7 cards
    hasPair = False # if you have a pair (EXACTLY 2 cards) and a three it triggers fullHouse and if you have a pair it checks your remaining cards for another one
    hasThree = False # also used for fullHouse trigger
    # these are necessary because your best hand may get overrode and these are permanent checks
    best = 0 # this is an int value from 0-8 that defines the initial value of the hand (defined in a text file)
    river.sort(reverse=True)
    hand5 = [card[0] for card in river[:5]] # your best 5 cards(the cards used by the best hand + however many high cards you need)
    msg = f"your best hand is a {read(river[0][0])} high card" # this is the player-readable message of their hand

    # Checks for flush
    big = [i[1] for i in river] # uses list comprehension to make a list of all suits aka index 1 of every item
    suit_counts = {} # dict for getting amount of a certain suit
    for suit in big:
        if suit in suit_counts:
            suit_counts[suit] += 1 # adds 1 to the relevant suit
        else:
            suit_counts[suit] = 1
    for suit, count in suit_counts.items(): # sees if you have a flush
        if count >= 5: 
            # finds all cards of that suit
            flush_cards = []
            for card in river: # finds the cards in the flush
                if card[1] == suit:
                    flush_cards.append(card[0])
            flush_cards.sort(reverse=True)
            hasFlush = True
            if best < 5: # this is a redundancy to make sure it gets the highest ranking combo.
                best = 5 # sets new highest
                msg = f"your best hand is a {read(flush_cards[0])} high flush" # Player message
                hand5 = flush_cards[:5] # since a flush requires 5 cards it simply adds these

    # Checks for single pair (most of this will be a repeat)
    big = [i[0] for i in river] # finds values instead of suits
    val_counts = {}
    for val in big:
        if val in val_counts:
            val_counts[val] += 1
        else:
            val_counts[val] = 1
    highest_two = None
    for val, count in val_counts.items(): # finds best pair
        if count == 2:
            if highest_two is None or val > highest_two:
                highest_two = val

    if highest_two is not None: # if it finds a pair:
        pair_cards = []
        for card in river:
            if card[0] == highest_two:
                pair_cards.append(card[0])
        pair_cards.sort(reverse=True)
        hasPair = True
        if best < 1:
            best = 1
            msg = f"your best hand is a {read(pair_cards[0])} high pair"
            river.sort(reverse=True)
            remaining_cards = [card[0] for card in river if card[0] not in pair_cards]
            hand5 = pair_cards + remaining_cards[:3] # hand5 is your pair cards plus your next three highest cards(excluding the pair cards cause those are already used)

    # Checks for 3 of a kind
    big = [i[0] for i in river] # finds values instead of suits
    val_counts = {}
    for val in big:
        if val in val_counts:
            val_counts[val] += 1
        else:
            val_counts[val] = 1
    highest_three = None
    for val, count in val_counts.items(): # finds best three
        if count == 3:
            if highest_three is None or val > highest_three:
                highest_three = val

    if highest_three is not None: # if it finds a pair:
        three_cards = []
        for card in river:
            if card[0] == highest_three:
                three_cards.append(card[0])
        three_cards.sort(reverse=True)
        hasThree = True
        if best < 3:
            best = 3
            msg = f"your best hand is a {read(three_cards[0])} high three of a kind"
            river.sort(reverse=True)
            remaining_cards = [card[0] for card in river if card[0] not in three_cards]
            hand5 = three_cards + remaining_cards[:2] # hand5 is your three cards plus your next three highest cards(excluding the pair cards cause those are already used)


    # Checks for four of a kind        
    big = [i[0] for i in river]
    val_counts = {}
    for val in big:
        if val in val_counts:
            val_counts[val] += 1
        else:
            val_counts[val] = 1
    for val, count in val_counts.items():
        if count == 4:
            four_cards = []
            for card in river:
                if card[0] == val:
                    four_cards.append(card[0])
            four_cards.sort(reverse=True)
            if best < 7:
                best = 7
                msg = f"your best hand is a {read(four_cards[0])} high Four of a Kind"
                river.sort(reverse=True)
                remaining_cards = [card[0] for card in river if card[0] not in four_cards]
                hand5 = four_cards + [remaining_cards[0]] # four cards plus a kicker

    # Checks for straight
    values = [card[0] for card in river] # this one is slightly different cause i wrote it first
    values = sorted(list(set(values)), reverse=True) # a sorted list of the unique values

    straight_count = 1 # value for later
    high_card = values[0] # starts high card as highest card
    straight_values = [values[0]]

    for i in range(1, len(values)): # checks every value except the first
        if values[i] == values[i-1] - 1: # if the value is 1 less than the previous:
            straight_count += 1 # one card closer to the straight
            straight_values.append(values[i]) # added to the list
            if straight_count >= 5: # once we have 5 weve got our straight
                if best < 4:
                    best = 4
                    msg = f"your best hand is a {read(straight_values[0])} high straight"
                    hand5 = straight_values

        else: # if one is out of order it tries again from the next card
            straight_count = 1
            high_card = values[i]
            straight_values = [values[i]]

    if 14 in values and 2 in values and 3 in values and 4 in values and 5 in values: # checks for ace low straight last because its the worst straight
        if best < 4:
            best = 4
            msg = f"your best hand is a 5 high straight"
            hand5 = [5,4,3,2,1,]
    # Finally we can check for product hands
    if hasThree and hasPair: # checks for full house
        if best < 6:
            best = 6
            msg = f"your best hand is a house of {read(three_cards[0])}s full of {read(pair_cards[0])}s"
            hand5 = three_cards + pair_cards
    if hasFlush: # checks flush cards for a straight
        values = flush_cards # this one is slightly different cause i wrote it first
        values = sorted(list(set(values)), reverse=True) # a sorted list of the unique values

        straight_count = 1 # value for later
        high_card = values[0] # starts high card as highest card
        straight_values = [values[0]]

        for i in range(1, len(values)): # checks every value except the first
            if values[i] == values[i-1] - 1: # if the value is 1 less than the previous:
                straight_count += 1 # one card closer to the straight
                straight_values.append(values[i]) # added to the list
                if straight_count >= 5: # once we have 5 weve got our straight
                    if best < 8:
                        best = 8
                        msg = f"your best hand is a {read(straight_values[0])} high straight flush"
                        hand5 = straight_values

            else: # if one is out of order it tries again from the next card
                straight_count = 1
                high_card = values[i]
                straight_values = [values[i]]

        if 14 in values and 2 in values and 3 in values and 4 in values and 5 in values: # checks for ace low straight last because its the worst straight
            if best < 8:
                best = 8
                msg = f"your best hand is a 5 high straight flush"
                hand5 = [5,4,3,2,1]
    if hasPair:
        big = [card[0] for card in river if card[0] not in pair_cards] # if the player has one pair it checks all cards except for those for a seconf pair
        firstPair = pair_cards
        val_counts = {}
        for val in big:
            if val in val_counts:
                val_counts[val] += 1
            else:
                val_counts[val] = 1
        highest_two = None
        for val, count in val_counts.items(): # finds best pair
            if count == 2:
                if highest_two is None or val > highest_two:
                    highest_two = val

        if highest_two is not None: # if it finds a pair:
            pair_cards = []
            for card in river:
                if card[0] == highest_two:
                    pair_cards.append(card[0])
            pair_cards.sort(reverse=True)
            hasPair = True
            if best < 2:
                best = 2
                river.sort(reverse=True)
                remaining_cards = [card for card in big if card not in pair_cards]
                hand5 = firstPair + pair_cards + [remaining_cards[0]] # hand5 is your pair cards plus your next three highest cards(excluding the pair cards cause those are already used)
                msg = f"your best hand is a {read(hand5[0])} high 2 pair"


    return {
    "rank":best,
    "used_cards":hand5,
    "msg":msg
            }

def compare(players): # this function finds a winner out of an indefinitely large list of players
    best_rank = -1 # this prevents a high card from tieing if it checks it first (this will be the best hand rank)
    best_hand = None # this will store the hand if kickers are needed to settle a tie
    winners = [] # in the case of a tie, the multiple winners will be stored here

    for person in players: 
        if person.check["rank"] > best_rank: # if the initial rank is the highest yet:
            best_rank = person.check["rank"]
            best_hand = person.check["used_cards"]
            winners = [person] # resets the winners list to just be them
        elif person.check["rank"] == best_rank: # if the initial rank ties:
            for i in range(len(best_hand)): # ranging it based on the length of the list allows i to be called as an identical index
                if person.check["used_cards"][i] > best_hand[i]: # if they have a better kicker:
                    best_hand = person.check["used_cards"]
                    winners = [person]
                    break
                elif person.check["used_cards"][i] < best_hand[i]: # if they have a worse kicker:
                    break
            else: # if there is a perfect tie:
                winners.append(person) # adds the person to the winners list. since they have the same rank and hand that doesnt need to be updated

    if len(winners) == 1:
        printb(f"Player {players.index(winners[0]) + 1} wins and gets {pot} chips") # this takes the index of the winning player and adds 1 to make the player number
    else:
        tied_players = [f"Player {players.index(i) + 1}" for i in winners]
        printb(f"It's a chopped pot between {', '.join(tied_players)}, they recieve {pot} chips each")
    return winners
def init_players(num_players, starting_chips=100): # this function initializes however many players you want
    return [Player(starting_chips) for i in range(num_players)] # it returns however many you want as a list with a default chip amount of 100

def init_game():
    while True:
        try:
            printb("\n\nEnter the number of players: ")
            num_players = int(input())
            if num_players not in range(2,7) and not dev:
                printb("too many / too few players")
                sleep(0.5)
                clear_console()
                continue # resets to the start of the loop
            break # valid input, breaks loop
        except ValueError:
            printb("Please enter a valid whole number")
            sleep(0.5)
            clear_console()
    return init_players(num_players)

def collect_blinds(players,dealer_pos):
    player_amount = len(players)
    small_blind_pos = (dealer_pos +1) % player_amount # this gets the index of the needed player using % to have it wrap around back to player 0
    big_blind_pos = (dealer_pos+2) % player_amount
    small_blind_player = players[small_blind_pos] # uses that index to get the object
    small_blind_pay = min(small_blind_amount, small_blind_player.chips) # amount to pay is the small blind amount or all of your money if your dont have enough
    small_blind_player.chips -= small_blind_pay # collects the pot
    pot = small_blind_pay # resets the pot
    
    printb(f"Player {small_blind_pos+1} posts small blind: {small_blind_pay}\n")
    if small_blind_pay < small_blind_amount:
        printb(f"Player {small_blind_pos + 1} is all-in")
        
    big_blind_player = players[big_blind_pos]
    big_blind_pay = min(big_blind_amount,big_blind_player.chips)
    big_blind_player.chips -= big_blind_pay
    pot += big_blind_pay

    printb(f"Player {big_blind_pos + 1} posts big blind: {big_blind_pay}\n")
    if big_blind_pay < big_blind_amount:
        printb(f"Player {big_blind_pos + 1} is all-in")

    return pot, small_blind_pos, big_blind_pos

def betting_round(players, starting_position, current_pot, current_bet=0): # this handles the betting rounds
    num_players = len(players)
    num_active = sum(1 for p in players if not p.folded and not p.all_in) # players that arent folded

    if num_active <= 1: # if theres only 1 player:
        return current_pot, current_bet

    position = starting_position # starting player
    last_raiser = -1 # last person to raise so it keeps looping until everyone calls
    rounds_completed = 0

    while True: # loops through all players
        # Skip folded or all-in players
        if players[position].folded or players[position].all_in:
            position = (position + 1) % num_players # this modulo % lets it loop through in a circle (i dont fully understand it to be honest). % returns the remainder of a division i think? something like that
            continue # this skips the rest of this run of the loop

        # Show table state
        clear_console() # this is so only the right player can see their cards
        printb(f"Player {position+1} press enter to continue: ")
        input() # this is used so it slow prints
        clear_console()
        printb(f"Current pot: ${current_pot}\n")
        printb(f"Current bet: ${current_bet}\n")
        for i, p in enumerate(players): # for index of player, and player object
            status = ""
            if p.folded:
                status = "(folded)"
            elif p.all_in:
                status = "(all-in)"
            else:
                status = f"(bet: ${p.current_bet})"

            printb(f"Player {i+1}: ${p.chips} {status}\n")

            # Show current player's hand
            if i == position: # if the current position is you:
                printb(f"Your hand: {', '.join(p.convertToStr())}\n") #display the cards
        printb(f"Table cards: {', '.join(card for card in table.convertToStr())}\n")

        # Player options
        player = players[position]
        to_call = current_bet - player.current_bet

        # Display options
        printb(f"\nPlayer {position+1}, it's your turn:\n")

        if to_call > 0:
            printb(f"1. Call ${to_call}\n")
            printb("2. Raise\n")
            printb("3. Fold\n")
        else:
            printb("1. Check\n")
            printb("2. Bet\n")
            printb("3. Fold\n")

        # Get player action
        try: # make sure they choose a valid option
            printb("Enter your choice (1-3): \n")
            action = int(input())

            # Handle call/check
            if action == 1:
                if to_call > 0:
                    # Call
                    if to_call >= player.chips:
                        # All-in call
                        printb(f"Player {position+1} calls ${player.chips} (all-in)\n")
                        current_pot += player.chips
                        player.current_bet += player.chips
                        player.chips = 0
                        player.all_in = True
                    else:
                        # Regular call
                        printb(f"Player {position+1} calls ${to_call}\n")
                        player.chips -= to_call
                        player.current_bet = current_bet
                        current_pot += to_call
                else:
                    # Check
                    printb(f"Player {position+1} checks\n")

            # Handle raise/bet
            elif action == 2:
                if to_call > 0:
                    prompt = "Enter raise amount (total bet, minimum double current bet): "
                    min_raise = current_bet * 2
                else:
                    prompt = f"Enter bet amount (minimum ${big_blind_amount}): "
                    min_raise = big_blind_amount
                printb(prompt)
                raise_amount = int(input())

                # Validate raise/bet amount
                if raise_amount < min_raise:
                    printb(f"Minimum raise/bet is ${min_raise}")
                    continue

                total_to_pay = raise_amount

                if total_to_pay >= player.chips:
                    # All-in raise
                    printb(f"Player {position+1} raises to ${player.chips} (all-in)")
                    current_pot += player.chips
                    player.current_bet += player.chips
                    current_bet = player.current_bet
                    player.chips = 0
                    player.all_in = True
                else:
                    # Regular raise
                    needed_chips = total_to_pay - player.current_bet
                    printb(f"Player {position+1} raises to ${total_to_pay}")
                    player.chips -= needed_chips
                    player.current_bet = total_to_pay
                    current_bet = total_to_pay
                    current_pot += needed_chips

                last_raiser = position

            # Handle fold
            elif action == 3:
                printb(f"Player {position+1} folds")
                player.folded = True
                num_active -= 1

                # Check if only one player left
                if num_active <= 1:
                    for i, p in enumerate(players):
                        if not p.folded:
                            printb(f"Player {i+1} wins ${current_pot} by default")
                            p.chips += current_pot
                            return 0, 0  # New pot is 0

            else:
                printb("Invalid option. Please choose 1-3.")
                continue

        except ValueError:
            printb("Please enter a valid number")
            sleep(1)
            continue

        # Move to next player
        position = (position + 1) % num_players

        if position == starting_position:
            rounds_completed += 1
            # If no one has raised and we've completed a round, end betting
            if last_raiser == -1 and rounds_completed >= 1:
                break

        # Check if betting round is complete due to everyone acting after a raise
        if position == last_raiser:
            break

    return current_pot, current_bet
def reset(players): # this function just sets the current bet to 0 before every new betting round
        for player in players:
            player.current_bet = 0

# Game Loop --------------------------------------------------------------------:

printb(f"welcome to...")
printb(r"""                                                        
                        88                              
                        88                              
                        88                              
8b,dPPYba,   ,adPPYba,  88   ,d8  ,adPPYba, 8b,dPPYba,  
88P'    "8a a8"     "8a 88 ,a8"  a8P_____88 88P'   "Y8  
88       d8 8b       d8 8888[    8PP88888// 88          
88b,   ,a8" "8a,   ,a8" 88`"Yba, "8b,   ,__ 88          
88`YbbdP"'   `"YbbdP"'  88   `Y8a `"Ybbd8"' 88          
88                                                      
88                                                      """,0.001)
while True:
    players = init_game()

    hand_running = True
    while hand_running:
        for player in players:
            player.hand = []
            player.current_bet = 0
            player.folded = False
            player.all_in = False
            player.check = []
        holdem = create_deck() # resetting all variables
        table = Player(0)
        table.hand = []
        pot = 0
        pot, small_blind_pos, big_blind_pos = collect_blinds(players,dealer_pos) # runs small and big blind
        first_to_act = (big_blind_pos + 1) % len(players)
        printb("\nDealing cards to players...\n")
        for player in players:
            draw(player)
            draw(player)
        printb(f"Small Blind: Player {small_blind_pos + 1}\n")
        printb(f"Big Blind: Player {big_blind_pos + 1}\n")
        printb(f"Current pot: {pot}\n")
        printb("\nPress Enter to continue to pre-flop betting...")        
        input()
        
        # Pre-flop betting - starts with player after big blind
        pot, current_bet = betting_round(players, first_to_act, pot, big_blind_amount)
        
        # Check if only one player remains
        active_players = [p for p in players if not p.folded]
        if len(active_players) <= 1:
            printb(f"\nPlayer {players.index(active_players[0]) + 1} wins ${pot}")
            active_players[0].chips += pot
        else:
            # Deal the flop (first 3 community cards)
            reset(players)
            printb("\nDealing the flop:")
            for _ in range(3):
                draw(table)
            printb("\nPress Enter to continue to flop betting...")
            input()
        
            # Flop betting - starts with small blind or first active player after dealer
            first_to_act = (dealer_pos + 1) % len(players)
            while first_to_act < len(players) and players[first_to_act].folded:
                first_to_act = (first_to_act + 1) % len(players)
        
            pot, current_bet = betting_round(players, first_to_act, pot)
        
            # Check if only one player remains after flop
            active_players = [p for p in players if not p.folded]
            if len(active_players) <= 1:
                printb(f"\nPlayer {players.index(active_players[0]) + 1} wins ${pot}")
                active_players[0].chips += pot
            else:
                # Deal the turn (4th community card)
                reset(players)
                printb("\nDealing the turn:")
                draw(table)
                printb("\nPress Enter to continue to turn betting...")
                input()
        
                # Turn betting
                pot, current_bet = betting_round(players, first_to_act, pot)
        
                # Check if only one player remains after turn
                active_players = [p for p in players if not p.folded]
                if len(active_players) <= 1:
                    printb(f"\nPlayer {players.index(active_players[0]) + 1} wins ${pot}")
                    active_players[0].chips += pot
                else:
                    # Deal the river (5th community card)
                    reset(players)
                    printb("\nDealing the river:")
                    draw(table)
                    printb("\nPress Enter to continue to river betting...")
                    input()
                    printb(f"Table cards: {', '.join(card for card in table.convertToStr())}\n")
                    pot, current_bet = betting_round(players, first_to_act, pot)
                    players_to_check = []
                    for i, player in enumerate(players):
                        printb(f"\n\nPlayer {i+1}'s hand:\n")
                        print(player)
                        player.check = showdown(player)
                        printb(player.check["msg"])
                        
                    winners = compare(players)
                    for i in winners:
                        split_amount = pot/len(winners)
                        i.chips += split_amount
                    dealer_position = (dealer_pos + 1) % len(players)
                    print("\nPlay another hand? (y/n): ")
                    another_hand = input().lower()
                    if another_hand != 'y':
                        hand_running = False
    print("\nStart a new game with different players? (y/n): ")
    new_game = input().lower()
    if new_game != 'y':
        break
printb("bye")
                    