import csv
import numpy as np
import os
import pandas as pd
import random


def standingRead(filename):
    """
    Input: filename of standing

    Reads teams and current standing data

    Returns two list (team and standing)
    """
    data = np.loadtxt(filename, delimiter=",", dtype=str).transpose().tolist()

    # Read as numpy array, transpose then convert to list
    data = np.loadtxt(filename, delimiter=",", dtype=str).transpose().tolist()

    # Check if loaded array is correct shape (2,16) array
    if np.shape(data)[0] != 2:
        raise Exception('Standings csv data should contain 2 columns (teams and standings)')

    if np.shape(data)[1] != 16:
        raise Exception('Standings csv data should contain 16 rows / team')

    teams = data[0]
    standings = [int(x) for x in data[1]]

    # Sort the data (create dataframe and sort by standing)
    dict = {'teams':teams, 'standings':standings}# Create data dictionary
    df = pd.DataFrame(dict).sort_values(by = 'standings', ascending=False)  

    return df['teams'].tolist(), df['standings'].tolist()


def readData(filename):
    """
    Reads csv file

    Return numpy array of shape (16, number of rounds, 3)
    Note: last dimension corresponds to [placement, kills, total points]
    """

    with open(filename) as file:

        csvreader = csv.reader(file, delimiter=',')

        # Placeholder: list of list of rows (for reading)
        rows = []

        for row in csvreader:

            # Initialize processedRow 
            # NOTE: processedRow is half the size of row: rank and kill for a game is combined to a tuple
            processedRow = []
            
            # Tuple value holder (stores value in creating tuples)
            placement = None
            kills = None
            
            # Create processed row
            # E.g. [2,8,4,9] will be converted to [(2,8), (4,9)]
            for index in range(len(row)):
                
                # Even case: Placement
                if index % 2 == 0:
                    placement = int(row[index])

                # Odd case: Kills & Total Points & Appending
                else:
                    kills = int(row[index])

                    # Create game with no points
                    points = 0

                    # Add placement points
                    if placement == 1:
                        points += 10
                    elif placement == 2:
                        points += 6
                    elif placement == 3:
                        points += 5
                    elif placement == 4:
                        points += 4
                    elif placement == 5:
                        points += 3
                    elif placement == 6:
                        points += 2
                    elif placement == 7 or placement == 8:
                        points += 1
                    # No added placement points outside top 8
                    else:
                        pass

                    # Add kill points
                    points += kills

                    processedRow.append((placement, kills, points))

            # Add processsed row to rows
            rows.append(processedRow)

    # Check if tournament has 16 placements
    if len(rows) != 16:
        raise Exception('Tournament should have 16 placements')

    # Convert data to numpy array 
    data = np.array(rows)            

    # Note data size is: (16, # of games, 3)
    return data


def compileData(folderName):
    """
    Combines all data from all files in folder - including subfolders
    Assumes csv file is in correct readable format
    Note: Calls readData function

    Returns numpy array of shape (16, number of rounds from all files)
    """

    # Initialize file name list
    filelist = []

    # Get all csv files in folder
    for root, dirs, files in os.walk(folderName):
        for file in files:
            #append the file name to the list
            if(file.endswith(".csv")):
                filelist.append(os.path.join(root,file))

    # Check if file is empty
    if len(filelist) == 0:
        raise Exception("No csv files found")

    # Initialize data
    dataExist = False # Used for initialization

    # Fill data variable
    for name in filelist:
        # Initialization case
        if dataExist == False:
            data = readData(name)
            dataExist = True
        # Concatenate data column wise
        else:
            data = np.concatenate((data, readData(name)), axis=1)

    return data


def smashSimulation(data, teams, standings, threshold, numTrials):
    """
    Output: probability of each team getting 1,2,3,4,5,6....16th place 
    
    Returns: 

    numpy array of results in win count format
    # Rows represent team, columns represent placement 

    List containing number of rounds until a champion wins
    """

    # Note results contains the information of how many times a team got / tally of a certain placement during simulation
    results = np.zeros((len(teams), len(teams)), dtype=int) 
    placements = list(range(len(teams)))
    totalGames = np.shape(data)[1]
    

    # Simulate tournaments
    # for _ in range(numTrials):
    for x in range(numTrials):

        if x % 10000 == 0:
            print(x)

        # Make copy of current standings
        standingsCopy = standings.copy()

        # Initialize winner indicator (Set to False: implies tournament is ongoing)
        winnerExist = False 

        # Simulate games
        while winnerExist == False:

            # Select random game - will be selected via index
            gameIndex = random.randint(0, totalGames - 1)
            gamePoints = data[:,gameIndex]

            # Shuffle placements (Teams will be assigned a random placement based from this list)
            np.random.shuffle(placements)

            # Check for teams over threshold (list of size 16 with 1/0 values: 1 means over threshold 0 below threshold)
            overThresholdBefore = [x >= threshold for x in standingsCopy]
            # Get indices of teams over the threshold
            indicesOverThreshold = [i for i in range(len(overThresholdBefore)) if overThresholdBefore[i] == 1]

            # Add points to current standing
            for k in range(16):
                standingsCopy[k] += gamePoints[placements[k]][2] # Adding points

            # Check if there are teams over the threshold that won

            # Extract placements from gamePoints array (will be a list of size 16)
            gamePlacement = gamePoints[:,0]

            # Important: Reorder gamePlacement extracted according to the earlier shuffled placements array
            gamePlacement = [gamePlacement[i] for i in placements]

            # Convert gamePlacement to a 1/0 array where 1 indicates winner, 0 for the rest
            gamePlacement = [1 if i == 1 else 0 for i in gamePlacement]

            # Get index of the winner
            winnerIndex = gamePlacement.index(1)

            # Check if winner index (of current round) is in indicesOverThreshold
            if winnerIndex in indicesOverThreshold:
                winnerExist = True
        
        # Initialize tournPlacement array (all zeroes)
        tournPlacement = [None] * 16

        # Assign first place to winner (note that 0 implies first place)
        tournPlacement[winnerIndex] = 0

        # Remove winner's score in standingsCopy array (so the rest of the teams can be ranked)
        # Removed since ranking is done by using the max function (Arbitrarily set to -1)
        standingsCopy[winnerIndex] = -1

        # Assign tournPlacement for the rest of the teams based on their score
        # range 15 - since 15 remaining teams
        for i in range(1,16):

            # Get index of the team with the max score
            maxIndex = standingsCopy.index(max(standingsCopy))

            # Remove winner's score in standingsCopy array (so the rest of the teams can be ranked)
            # Removed since ranking is done by using the max function (Arbitrarily set to -1)
            standingsCopy[maxIndex] = -1

            # Assign tournPlacement
            tournPlacement[maxIndex] = i

        # Add placement to result
        for k in range(16):
            results[k][tournPlacement[k]] += 1

    return results


def main():
    pass


if __name__ == "__main__":
    main()

