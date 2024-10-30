import csv
import numpy as np
import os

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

    # Note data size is: (16, # of games, 2)
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


def main():
    pass


if __name__ == "__main__":
    main()


