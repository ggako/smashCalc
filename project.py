import csv
import numpy as np

def readData(filename):
    """
    Reads csv file

    Return numpy array of shape (16, number of rounds, 2)
    Note: last dimension corresponds to [placement, kills]
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

                # Odd case: Kills
                else:
                    kills = int(row[index])
                    processedRow.append((placement, kills))

            # Add processsed row to rows
            rows.append(processedRow)

    # Check if tournament has 16 placements
    if len(rows) != 16:
        raise Exception('Tournament should have 16 placements')

    # Convert data to numpy array 
    data = np.array(rows)            

    # Note data size is: (16, # of games, 2)
    return data

