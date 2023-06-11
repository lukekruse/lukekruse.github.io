import numpy as np
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt


# Global variables
xlsFile = 'ShuffleData.xlsx'
DF = pd.read_excel(xlsFile, sheet_name='data')

#-------------------------------------------------------------------------------
class Deck:
    def __init__(self, size = 100, deckType = 'data', deckID = 3, shuffles = None):
        self.size = size
        self.deckType = deckType

        # Initial ordering of cards
        # First item in list is the BOTTOM card in the deck when the deck is 
        # facedown
        self.orders = [[]]
        self.cards = []
        for card_num in range(self.size):
            self.orders[0].append(self.size - card_num)
            self.cards.append(self.size - card_num)
    
        # If the deck is from a dataset, get the shuffle data 
        if self.deckType == 'data':
            self.deckID = deckID
            df = DF[DF.sample_id == self.deckID]
            
            self.shuffles = len(list(set(df.shuffle_id)))
            for shuffleID in range(1, self.shuffles + 1):
                tmpOrder = []
                tmpDf = df[df.shuffle_id == shuffleID]

                for columnName in self.cards:
                    tmpOrder.append(list(tmpDf[columnName])[0])
                self.orders.append(tmpOrder)
            print(f'Total shuffles found for deck {self.deckID}: {self.shuffles}')
            self.cutSizes = []
            cutCardNums = list(df.first_inserted_card_number)
            self.cutCardNums = cutCardNums 
            for shuffleID, cardNum in enumerate(cutCardNums):
                self.cutSizes.append(self.size - self.orders[shuffleID].index(
                    cardNum))


        elif self.deckType == 'model':
            self.deckID = None
            self.shuffles = shuffles
    
    #--------------------------------------------------------------------------- 
    def randomShuffler(self):
        for shuffle in range(self.shuffles):
            np.random.shuffle(self.cards)
            self.orders.append(list(self.cards))
    
    
    #--------------------------------------------------------------------------- 
    def parseShuffles(self):
        '''
        PURPOSE:
        Analyzes and compile shuffle data

        OUTPUTS:

        cardPosition = {card_num : [list of positions]}
            Track where a specific card goes through the deck after each shuffle
        
        nextPosition = {position(0) : num_shuffles, t : [list of positions(t)]}
            Track where a card in a certain position is likely to go after t
                shuffles
        
        '''
        # Initialize outputs
        cardPosition = {}
        nextPosition = {}
        for cardNum in self.cards:
            cardPosition[cardNum] = []
            nextPosition[cardNum] = {}
       
        for shuffle in range(self.shuffles):
            order = self.orders[shuffle]
            for cardNum in self.cards:
                cardPosition[cardNum].append(self.size - order.index(cardNum))
                if shuffle != 0: 
                    nextPosition[cardNum][shuffle] = []
        
        for position in self.cards:
            for cardNum, visitedPositions in cardPosition.items():
                try:
                    # Find each frame that the card visited the specific position
                    framesVisited = [i for i, val in enumerate(visitedPositions)\
                        if val == position]
                    for frameVisited in framesVisited:
                        for t in range(self.shuffles - frameVisited - 1):
                            nextPosition[position][t + 1].append(
                                visitedPositions[frameVisited + t + 1]
                                )
                
                except ValueError:
                    pass
        
        self.cardPos = cardPosition
        self.nextPos = nextPosition
    #--------------------------------------------------------------------------- 
    def extractInterlacing(self):
        '''
        PURPOSE:
        Extracts information regarding the interlacing from one deck order to
        the next.

        PREVIOUS PROBLEMS:
        The data need to be in the correct shuffle order in the data sheet for
        this to function properly

        '''
        data = {}
        for shuffleID in range(1, self.shuffles):
            data[shuffleID] = []
            
            cutIndex = self.size - self.cutSizes[shuffleID-1] 
            pile1 = self.orders[shuffleID - 1][:cutIndex]
            pile2 = self.orders[shuffleID - 1][cutIndex:]
            
            count = 0
            curPile = None

            for card in self.orders[shuffleID]:
                if card in pile1:
                    if curPile == 1:
                        count += 1
                    else:
                        if not curPile == None:
                            data[shuffleID].append((curPile, count))
                        # Reset current pile and count
                        curPile = 1
                        count = 1
                elif card in pile2:
                    if curPile == 2:
                        count += 1
                    else:
                        if not curPile == None:
                            data[shuffleID].append((curPile, count))
                        curPile = 2
                        count = 1

                if card == self.orders[shuffleID][-1]:
                    data[shuffleID].append((curPile, count))
        self.interlacing = data

#-------------------------------------------------------------------------------
class Analyze:
    def __init__(self, decks):
        

        if isinstance(decks, list):
            self.numDecks = len(decks)
            self.decks = decks
        else:
            self.numDecks = 1
            self.decks = [ decks ]
            

    #--------------------------------------------------------------------------- 
    def plotDistribution(self, option = 'cut'):
       
        data = []
        for deck in self.decks:
            if option == 'cut':
                data.extend(deck.cutSizes)

            elif option == 'interlacing':
                deck.extractInterlacing()
                tmp = deck.interlacing
                for _, vals in tmp.items():
                    for val in vals:
                        (_, i) = val
                        data.append(i)

            elif option == 'nextPos':
                deck.parseShuffles()
                tmp = deck.nextPos
                pos, shuffles = 2, 10
                data.extend(tmp[pos][shuffles])
            
        d = 1
        bins = [0.5 + d*i for i in range(int(100/d)+1)]
        #bins = [0.5 + 5*i for i in range(21)]
        plt.hist(data, bins = bins)
        plt.show()

    #--------------------------------------------------------------------------- 
    def plotMultipleDistributions(self, pos = 50, shuffles = [1, 2,3,4,5], 
        autoBinning = False, d = 1):
        data = {}
        for deck in self.decks:
            deck.parseShuffles()
            tmp =deck.nextPos
            #for shuffle in range(1, maxShuffles+1):
            for shuffle in shuffles:
                try:
                    try:
                        tmp[pos][shuffle]
                        data[shuffle].extend(tmp[pos][shuffle])
                    except KeyError:
                        data[shuffle] = tmp[pos][shuffle]
                except KeyError:
                    pass
                    #data[shuffle] = tmp[pos][shuffle]

        for i, shuffle in enumerate(data.keys()):
            if not autoBinning:
                # Manual Binning

                bins = [0.5 + d*i for i in range(int(100/d)+1)]
                x = [i*d for i in range(1, int( 100/d) + 1)]
                pdx, _ = np.histogram(data[shuffle], bins = bins, density = True)
                y = pdx*d #+ i/2
                plt.plot(x, y, label = f'{shuffle} Shuffles')
            else:
                # Auto binning
                pdx, bins = np.histogram(data[shuffle], density = True)
                d = bins[1] - bins[0]
                x = [xi + d for xi in bins[:-1]]
                y = pdx*d #+ i/4
                print(shuffle, np.sum(y))
                plt.plot(x, y, label = f'{shuffle} Shuffles')

        plt.plot([1, 100], [0.01, 0.01], 'r--', label='Equally Probable')
        plt.legend()
        
        plt.xlabel('Position within deck')
        plt.ylabel(f'Likelihood to find a card originally at position {pos} at a new position')
        plt.xlim(1, 100)
        #plt.ylim(0, 1)


    #--------------------------------------------------------------------------- 
    def plotEntropy(self, positions = [1, 2, 25, 50, 75, 100]):

        for pos in positions:
            data = {}
            for deck in self.decks:
                deck.parseShuffles()
                tmp = deck.nextPos
                for shuffle in tmp[pos].keys():
                    if shuffle <= deck.shuffles/2:
                        if shuffle <= 25:
                            try:
                                data[shuffle].extend(tmp[pos][shuffle])
                            except KeyError:
                                data[shuffle] = tmp[pos][shuffle]

            
            #bins = [0.5 + i for i in range(101)]
            #d = 1
            bins = [0.5 + 5*i for i in range(21)]
            d = 5
            
            x = data.keys()
            y = []
            for key, vals in data.items():
                ps, _ = np.histogram(vals, bins = bins, density = True)

                S = 0.
                for p in ps:
                    if p != 0.:
                        S += -p*d*np.log(p*d)
                
                Smax = np.log(100/d)
                y.append(S/Smax)

            plt.plot(x, y, label=f'Initial Position: {pos}')
        plt.legend()

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    #deckIDs = [1,2]
    #deckIDs = [3]
    #deckIDs = [4]
    deckIDs = [1,2,3]
    #deckIDs = [1,2,3,4]
    decks = []
    for deckID in deckIDs:
        
        deck = Deck(deckID = deckID, size = 100)
        #deck.parseShuffles()
        #deck.extractInterlacing()
        #raise SystemExit
        decks.append(deck)

    analysis = Analyze(decks = decks)
    #analysis.plotDistribution(option = 'cut')
    analysis.plotDistribution(option = 'interlacing')
    #analysis.plotDistribution(option = 'nextPos')
    #analysis.plotEntropy(positions = [1,2, 78,80])
    #analysis.plotEntropy()
    #analysis.plotMultipleDistributions(d=1)

    '''
    deck = Deck(deckType = 'model', shuffles = 500)
    deck.randomShuffler() 
    analysis = Analyze(decks = [deck])
    analysis.plotEntropy()
    '''
    plt.show()

















