import pygame, sys, random, copy
import numpy
from pygame.locals import *
from cards import *

def genCard(cList, xList):
    # generate and remove an card from cList and append it to xList.
    # return the card, and whether the card is an Ace
    cA = 0
    card = random.choice(cList)
    cList.remove(card)
    xList.append(card)
    if card in cardA:
        cA = 1
    return card, cA

def initGame(cList, uList, dList):
    # generates two cards for dealer and user, one at a time for each.
    # returns if card is Ace and the total amount of the cards per person.
    userA = 0
    dealA = 0
    card1, cA = genCard(cList, uList)
    userA += cA
    card2, cA = genCard(cList, dList)
    dealA += cA
    dealAFirst = copy.deepcopy(dealA)
    card3, cA = genCard(cList, uList)
    userA += cA
    card4, cA = genCard(cList, dList)
    dealA += cA
    # the values are explained below when calling the function
    return getAmt(card1) + getAmt(card3), userA, getAmt(card2) + getAmt(card4), dealA, getAmt(card2), dealAFirst

def make_state(userSum, userA, dealFirst, dealAFirst):
    # check whether the user has Ace cards
    if userSum > 21:
        if userA > 0:
            # turn the Ace cards value from 11 to 1 if necessary
            while userSum > 21 and userA > 0:
                userSum = userSum - 10
                userA = userA - 1
    # eliminate duplicated bust cases
    if userSum > 21:
        userSum = 22
    # userSum: sum of user's cards
    # userA: number of user's Aces
    # dealFirst: value of dealer's first card
    # dealAFirst: whether dealer's first card is Ace
    return (userSum, userA, dealFirst, dealAFirst)

def pick_action(hit, stand, epsilon):
    # generate a number in range (0, 1)
    num = random.uniform(0, 1)
    # choose a random action if the number is less than epsilon
    if num < epsilon:
        return random.randint(0, 1)
    # else choose the best action
    else:
        if hit >= stand:
            # 0 represents hit
            return 0
        else:
            # 1 represents stand
            return 1

def main():
    ccards = copy.copy(cards)
    stand = False
    userCard = []
    dealCard = []
    winNum = 0
    loseNum = 0
    # initialize game
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Blackjack')
    font = pygame.font.SysFont("", 20)
    hitTxt = font.render('Hit', 1, black)
    standTxt = font.render('Stand', 1, black)
    restartTxt = font.render('Restart', 1, black)
    MCTxt = font.render('MC', 1, blue)
    TDTxt = font.render('TD', 1, blue)
    QLTxt = font.render('QL', 1, blue)
    gameoverTxt = font.render('End of Round', 1, white)
    # prepare table of utilities
    MCvalues = {}
    TDvalues = {}
    Qvalues = {}
    # i iterates through the sum of user's cards. It is set to 22 if the user went bust.
    # j iterates through the value of the dealer's first card. Ace is eleven.
    # a1 is the number of Aces that the user has.
    # a2 denotes whether the dealer's first card is Ace.
    for i in range(2,23):
        for j in range(2,12):
            for a1 in range(0,5):
                for a2 in range(0,2):
                    s = (i, a1, j, a2)
                    # utility computed by MC-learning
                    MCvalues[s] = 0.0
                    # utility computed by TD-learning
                    TDvalues[s] = 0.0
                    # first element is Q value of "Hit", second element is Q value of "Stand"
                    Qvalues[s] = [0.0, 0.0]
    # userSum: sum of user's cards
    # userA: number of user's Aces
    # dealSum: sum of dealer's cards (including hidden one)
    # dealA: number of all dealer's Aces,
    # dealFirst: value of dealer's first card
    # dealAFirst: whether dealer's first card is Ace
    userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
    state = make_state(userSum, userA, dealFirst, dealAFirst)
    # fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((80, 150, 15))
    hitB = pygame.draw.rect(background, gray, (10, 445, 75, 25))
    standB = pygame.draw.rect(background, gray, (95, 445, 75, 25))
    MCB = pygame.draw.rect(background, white, (180, 445, 75, 25))
    TDB = pygame.draw.rect(background, white, (265, 445, 75, 25))
    QLB = pygame.draw.rect(background, white, (350, 445, 75, 25))
    autoMC = False
    autoTD = False
    autoQL = False
    # event loop
    while True:
        # Our state information does not take into account of number of cards
        # So it's ok to ignore the rule of winning if getting 5 cards without going bust
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        # MC Learning
        # compute the utilities of all states under the policy "Always hit if below 17"
        if autoMC:
            # dictionary that maps state to the sequence of reward values
            Gvalues = {}
            # initialize the dictionary
            for s in MCvalues:
                Gvalues[s] = []
            i = 0
            while i < 600:
                # make copies of the cards for simulation
                cards_sim = copy.copy(ccards)
                userCards_sim = copy.copy(userCard)
                dealCards_sim = copy.copy(dealCard)
                # make a copy of the current state for simulation
                state_sim = copy.deepcopy(state)
                # initialize the episode
                episode = []
                # generate an episode following the policy
                while True:
                    # append the state to the episode
                    episode.append(state_sim)
                    # stand when sum is not less than 17
                    if state_sim[0] >= 17:
                        break
                    # ask for a new card
                    card, cA = genCard(cards_sim, userCards_sim)
                    # update the state
                    state_sim = make_state(state_sim[0] + getAmt(card), state_sim[1] + cA, state_sim[2], state_sim[3])
                # get the sum of terminal state
                userSum_sim = state_sim[0]
                # initialize the reward
                reward = 0.0
                # reward is -1 if user busts
                if userSum_sim > 21:
                    reward = -1.0
                # get the sum of dealer cards
                else:
                    # get the first card of dealer 
                    dealSum_sim = copy.deepcopy(dealFirst)
                    # get the current number of Ace cards dealer has
                    dealA_sim = copy.deepcopy(dealAFirst)
                    # simulate the dealer
                    while dealSum_sim <= userSum_sim and dealSum_sim < 17:
                        # ask for a new card
                        card, cA = genCard(cards_sim, dealCards_sim)
                        # update the number of Ace cards the dealer has
                        dealA_sim = dealA_sim + cA
                        # update the sum of cards the dealer has
                        dealSum_sim = dealSum_sim + getAmt(card)
                        # turn the Ace cards value from 11 to 1 if necessary
                        while dealSum_sim > 21 and dealA_sim > 0:
                            # update the number of Ace cards the dealer has
                            dealA_sim = dealA_sim - 1
                            # update the sum of cards the dealer has
                            dealSum_sim = dealSum_sim - 10
                    # reward is 1 if dealer busts
                    if dealSum_sim > 21:
                        reward = 1.0
                    # compare the sums between user and dealer
                    else:
                        # reward is -1 if dealer has larger sum
                        if dealSum_sim > userSum_sim:
                            reward = -1.0
                        # reward is 1 if user has larger sum
                        elif dealSum_sim < userSum_sim:
                            reward = 1.0
                # reverse the episode
                reverse_episode = episode[::-1]
                # calculate the reward for each state
                reward = reward * 0.9
                for s in reverse_episode:
                    # append the reward to the dictionary for each state
                    Gvalues[s].append(reward)
                    # apply the discount factor
                    reward = reward * 0.9
                # calculate the average
                for s in episode:
                    MCvalues[s] = numpy.mean(Gvalues[s])
                i = i + 1
            # print(MCvalues[state])
        # TD Learning
        # compute the utilities of all states under the policy "Always hit if below 17"
        if autoTD:
            # dictionary that maps state to the number of times this state gets visited
            visited = {}
            # initialize the dictionary
            for s in TDvalues:
                visited[s] = 0.0
            i = 0
            while i < 600:
                # make copies of the cards for simulation
                cards_sim = copy.copy(ccards)
                userCards_sim = copy.copy(userCard)
                dealCards_sim = copy.copy(dealCard)
                # make a copy of the current state for simulation
                state_sim = copy.deepcopy(state)
                while True:
                    # increment the number of times this state gets visited
                    visited[state_sim] = visited[state_sim] + 1.0
                    # stand when sum is not less than 17
                    if state_sim[0] >= 17:
                        break
                    # ask for a new card
                    card, cA = genCard(cards_sim, userCards_sim)
                    # create the next state
                    nextState_sim = make_state(state_sim[0] + getAmt(card), state_sim[1] + cA, state_sim[2], state_sim[3])
                    # get the learning rate
                    alpha = 10.0 / (9.0 + visited[state_sim])
                    # apply the temporal difference
                    TDvalues[state_sim] = TDvalues[state_sim] + alpha * (0.9 * TDvalues[nextState_sim] - TDvalues[state_sim])
                    # go to the next state
                    state_sim = nextState_sim
                # get the sum of terminal state
                userSum_sim = state_sim[0]
                # initialize the reward
                reward = 0.0
                # reward is -1 if user busts
                if userSum_sim > 21:
                    reward = -1.0
                # get the sum of dealer cards
                else:
                    # get the first card of dealer 
                    dealSum_sim = copy.deepcopy(dealFirst)
                    # get the current number of Ace cards dealer has
                    dealA_sim = copy.deepcopy(dealAFirst)
                    # simulate the dealer
                    while dealSum_sim <= userSum_sim and dealSum_sim < 17:
                        # ask for a new card
                        card, cA = genCard(cards_sim, dealCards_sim)
                        # update the number of Ace cards the dealer has
                        dealA_sim = dealA_sim + cA
                        # update the sum of cards the dealer has
                        dealSum_sim = dealSum_sim + getAmt(card)
                        # turn the Ace cards value from 11 to 1 if necessary
                        while dealSum_sim > 21 and dealA_sim > 0:
                            # update the number of Ace cards the dealer has
                            dealA_sim = dealA_sim - 1
                            # update the sum of cards the dealer has
                            dealSum_sim = dealSum_sim - 10
                    # reward is 1 if dealer busts
                    if dealSum_sim > 21:
                        reward = 1.0
                    # compare the sums between user and dealer
                    else:
                        # reward is -1 if dealer has larger sum
                        if dealSum_sim > userSum_sim:
                            reward = -1.0
                        # reward is 1 if user has larger sum
                        elif dealSum_sim < userSum_sim:
                            reward = 1.0
                # get the learning rate
                alpha = 10.0 / (9.0 + visited[state_sim])
                # apply the temporal difference
                TDvalues[state_sim] = TDvalues[state_sim] + alpha * (0.9 * reward - TDvalues[state_sim])
                i = i + 1
            # print(TDvalues[state])
        # Q-Learning
        # For each state, compute the Q value of the action "Hit" and "Stand"
        if autoQL:
            # dictionary that maps state to the number of times this state gets visited
            visited = {}
            # initialize the dictionary
            for s in Qvalues:
                visited[s] = 0.0
            i = 0
            while i < 600:
                # make copies of the cards for simulation
                cards_sim = copy.copy(ccards)
                userCards_sim = copy.copy(userCard)
                dealCards_sim = copy.copy(dealCard)
                # make a copy of the current state for simulation
                state_sim = copy.deepcopy(state)
                # generate the epsilon
                epsilon = random.uniform(0, 0.5)
                while True:
                    # increment the number of times this state gets visited
                    visited[state_sim] = visited[state_sim] + 1.0
                    # pick an action
                    action = pick_action(Qvalues[state_sim][0], Qvalues[state_sim][1], epsilon)
                    # if the action is stand
                    if action == 1:
                        break
                    # if the sum is greater than 21
                    if state_sim[0] > 21:
                        break
                    # ask for a new card
                    card, cA = genCard(cards_sim, userCards_sim)
                    # create the next state
                    nextState_sim = make_state(state_sim[0] + getAmt(card), state_sim[1] + cA, state_sim[2], state_sim[3])
                    # get the learning rate
                    alpha = 10.0 / (9.0 + visited[state_sim])
                    # apply the Q learning equation
                    Qvalues[state_sim][0] = Qvalues[state_sim][0] + alpha * (0.9 * max(Qvalues[nextState_sim][0], Qvalues[nextState_sim][1]) - Qvalues[state_sim][0])
                    # go to the next state
                    state_sim = nextState_sim
                # get the sum of terminal state
                userSum_sim = state_sim[0]
                # initialize the reward
                reward = 0.0
                # reward is -1 if user busts
                if userSum_sim > 21:
                    reward = -1.0
                # get the sum of dealer cards
                else:
                    # get the first card of dealer
                    dealSum_sim = copy.deepcopy(dealFirst)
                    # get the current number of Ace cards dealer has
                    dealA_sim = copy.deepcopy(dealAFirst)
                    # simulate the dealer
                    while dealSum_sim <= userSum_sim and dealSum_sim < 17:
                        # ask for a new card
                        card, cA = genCard(cards_sim, dealCards_sim)
                        # update the number of Ace cards the dealer has
                        dealA_sim = dealA_sim + cA
                        # update the sum of cards the dealer has
                        dealSum_sim = dealSum_sim + getAmt(card)
                        # turn the Ace cards value from 11 to 1 if necessary
                        while dealSum_sim > 21 and dealA_sim > 0:
                            # update the number of Ace cards the dealer has
                            dealA_sim = dealA_sim - 1
                            # update the sum of cards the dealer has
                            dealSum_sim = dealSum_sim - 10
                    # reward is 1 if dealer busts
                    if dealSum_sim > 21:
                        reward = 1.0
                    # compare the sums between user and dealer
                    else:
                        # reward is -1 if dealer has larger sum
                        if dealSum_sim > userSum_sim:
                            reward = -1.0
                        # reward is 1 if user has larger sum
                        elif dealSum_sim < userSum_sim:
                            reward = 1.0
                # get the learning rate
                alpha = 10.0 / (9.0 + visited[state_sim])
                # apply the Q learning equation
                Qvalues[state_sim][1] = Qvalues[state_sim][1] + alpha * (0.9 * reward - Qvalues[state_sim][1])
                i = i + 1
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #Clicking the white buttons can start or pause the learning processes
            elif event.type == pygame.MOUSEBUTTONDOWN and MCB.collidepoint(pygame.mouse.get_pos()):
                autoMC = not autoMC
            elif event.type == pygame.MOUSEBUTTONDOWN and TDB.collidepoint(pygame.mouse.get_pos()):
                autoTD = not autoTD
            elif event.type == pygame.MOUSEBUTTONDOWN and QLB.collidepoint(pygame.mouse.get_pos()):
                autoQL = not autoQL
            elif event.type == pygame.MOUSEBUTTONDOWN and (gameover or stand):
                #restarts the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
            elif event.type == pygame.MOUSEBUTTONDOWN and not (gameover or stand) and hitB.collidepoint(pygame.mouse.get_pos()):
                #Give player a card
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameover and standB.collidepoint(pygame.mouse.get_pos()):
                #Dealer plays, user stands
                stand = True
                if dealSum == 21:
                    pass
                else:
                    while dealSum <= userSum and dealSum < 17:
                        card, cA = genCard(ccards, dealCard)
                        dealA += cA
                        dealSum += getAmt(card)
                        while dealSum > 21 and dealA > 0:
                            dealA -= 1
                            dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        MCU = font.render('MC-Utility of Current State: %f' % MCvalues[state], 1, black)
        TDU = font.render('TD-Utility of Current State: %f' % TDvalues[state], 1, black)
        QV = font.render('Q values: (Hit) %f (Stand) %f' % tuple(Qvalues[state]) , 1, black)
        winTxt = font.render('Wins: %i' % winNum, 1, white)
        loseTxt = font.render('Losses: %i' % loseNum, 1, white)
        screen.blit(background, (0, 0))
        screen.blit(hitTxt, (39, 448))
        screen.blit(standTxt, (116, 448))
        screen.blit(MCTxt, (193, 448))
        screen.blit(TDTxt, (280, 448))
        screen.blit(QLTxt, (357, 448))
        screen.blit(winTxt, (550, 423))
        screen.blit(loseTxt, (550, 448))
        screen.blit(MCU, (20, 200))
        screen.blit(TDU, (20, 220))
        screen.blit(QV, (20, 240))
        for card in dealCard:
            x = 10 + dealCard.index(card) * 110
            screen.blit(card, (x, 10))
        screen.blit(cBack, (120, 10))
        for card in userCard:
            x = 10 + userCard.index(card) * 110
            screen.blit(card, (x, 295))
        if gameover or stand:
            screen.blit(gameoverTxt, (270, 200))
            screen.blit(dealCard[1], (120, 10))
        pygame.display.update()

if __name__ == '__main__':
    main()
