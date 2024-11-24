import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

def check_csv_file_with_pandas(file_path: str):
    """
    Checks if the given file is a valid CSV file by attempting to read it with pandas.

    Parameters:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if the file is a valid CSV file, False otherwise.
    """
    try:
        # Attempt to read the file with pandas
        pd.read_csv(file_path)
        return True
    except FileNotFoundError:
        return False
    except pd.errors.ParserError:
        return False
    except Exception as e:
        return False

def process_csv(file_path: str):
    """
    Processes a CSV file containing user activity times and transforms the time data
    into numerical features suitable for analysis.

    The function reads a CSV file where each row represents a user and their activity 
    time. It computes the time in seconds from midnight, as well as sine and cosine 
    transformations of the time, which are useful for circular data representation.

    Parameters:
        file_path (str): The path to the CSV file. The file is expected to have two columns:
                         - "Users": A string identifier for each user.
                         - "Times": Time of activity in the format HH:MM:SS.

    Returns:
        pandas.DataFrame: A DataFrame with the following columns:
            - "Users": Original user identifiers.
            - "Times": Original time data converted to pandas datetime format.
            - "Seconds_from_midnight": Time in seconds from midnight (0 to 86399).
            - "Time_sin": Sine transformation of time for circular representation.
            - "Time_cos": Cosine transformation of time for circular representation.

    Example:
        Input CSV:
            User1,12:34:56
            User2,08:45:12

        Output DataFrame:
            Users               Times  Seconds_from_midnight  Time_sin  Time_cos
            User1 2023-01-01 12:34:56                  45296  0.984808 -0.173648
            User2 2023-01-01 08:45:12                  31512  0.707107  0.707107
    """
    df = pd.read_csv(file_path, header=0, names=["Users", "Times"])
    df["Times"] = pd.to_datetime(df["Times"], format="%H:%M:%S")
    df["Seconds_from_midnight"] = (df["Times"].apply(lambda t: t.hour * 3600 + t.minute * 60 + t.second))
    df["Time_sin"] = np.sin(2 * np.pi * df["Seconds_from_midnight"] / 86400)
    df["Time_cos"] = np.cos(2 * np.pi * df["Seconds_from_midnight"] / 86400)
    return df

def obtain_euclidean_distance_array(df):
    """
    Computes the Euclidean distance between users based on sine and cosine transformations
    of their activity times.

    The function groups the input DataFrame by user, averages the sine and cosine 
    transformations of their activity times, and calculates pairwise Euclidean distance 
    between these average time vectors.

    Parameters:
        df (pandas.DataFrame): A DataFrame containing the following columns:
            - "Users": User identifiers (grouping key).
            - "Time_sin": Sine transformation of time for circular representation.
            - "Time_cos": Cosine transformation of time for circular representation.

    Returns:
        tuple: A tuple containing:
            - numpy.ndarray: A 2D array where each element (i, j) represents the 
              Euclidean distance between user `i` and user `j`.
            - pandas.DataFrame: A DataFrame with averaged sine and cosine time 
              values for each user. Columns:
                - "Users": User identifiers.
                - "Time_sin": Averaged sine values of activity times.
                - "Time_cos": Averaged cosine values of activity times.
    """
    df_time_vectors = df.groupby("Users")[["Time_sin", "Time_cos"]].mean().reset_index()
    
    # Calculate pairwise Euclidean distances
    user_distance_array = cdist(df_time_vectors[["Time_sin", "Time_cos"]], df_time_vectors[["Time_sin", "Time_cos"]], metric="euclidean")
    
    return user_distance_array, df_time_vectors



def lowest_distance_pair(user_distance_array, df_time_vectors):
    """
    Identifies the pair of users with the smallest Euclidean distance.

    This function creates a DataFrame to represent the Euclidean distances between 
    users, excludes diagonal values (which represent self-distance), and determines 
    the pair of users with the minimum distance.

    Parameters:
        user_distance_array (numpy.ndarray): A 2D array where each element (i, j) 
            represents the Euclidean distance between user `i` and user `j`.
        df_time_vectors (pandas.DataFrame): A DataFrame containing:
            - "Users": User identifiers.

    Returns:
        tuple: A tuple containing:
            - str: Identifier of the first user in the closest pair (smallest distance).
            - str: Identifier of the second user in the closest pair.
            - float: The smallest Euclidean distance value between the two users.
    """
    user_distance_df = pd.DataFrame(user_distance_array, index=df_time_vectors["Users"],  columns=df_time_vectors["Users"])
    
    mask = np.eye(user_distance_df.shape[0], dtype=bool)  # Eye matrix will be True for the diagonal
    masked_distance = user_distance_df.values.copy()
    masked_distance[mask] = np.inf  # Set diagonal values to infinity to exclude them

    min_dist_index = np.unravel_index(np.argmin(masked_distance), masked_distance.shape)  # Find min distance
    user1 = user_distance_df.index[min_dist_index[0]]  # User 1
    user2 = user_distance_df.columns[min_dist_index[1]]  # User 2
    min_distance_value = masked_distance[min_dist_index]  # Minimum distance value
    
    return user1, user2, min_distance_value


def compute_lowest_distance_from_csv(file_path):
    """
    Computes the pair of users with the smallest Euclidean distance from a CSV file.

    This function checks if the provided file is a valid CSV, processes the data to 
    calculate sine and cosine representations of user times, computes Euclidean distance 
    between users, and identifies the pair of users with the smallest distance.

    Parameters:
        file_path (str): The path to the CSV file containing user data with columns:
            - "Users": User identifiers.
            - "Times": Time values in "HH:MM:SS" format.

    Returns:
        tuple: A tuple containing:
            - str: Identifier of the first user in the closest pair.
            - str: Identifier of the second user in the closest pair.
            - float: The smallest Euclidean distance between the two users.

    Notes:
        If the file is not a valid CSV, or if there is an issue during processing, 
        the function prints an error message instead of returning a result.

    Example:
        Input:
            file_path: "Users Info.csv"

        Output:
            ("User1", "User2", 0.95)
    """
    check_result = check_csv_file_with_pandas(file_path)
    if check_result == True:
        df = process_csv(file_path)
        user_distance_array, df_time_vectors = obtain_euclidean_distance_array(df)  # Updated function for Euclidean distance
        user1, user2, min_distance_value = lowest_distance_pair(user_distance_array, df_time_vectors)  # Updated pair finder
        return user1, user2, min_distance_value
    else:
        print("Inappropriate file")