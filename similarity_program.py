import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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
            Users,Times
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


def obtain_cosine_similarity_array(df):
    """
    Computes cosine similarity between user activity times based on sine and cosine 
    transformations of time data.

    The function groups the input DataFrame by user, averages the sine and cosine 
    transformations of their activity times, and calculates pairwise cosine similarity 
    between these average time vectors.

    Parameters:
        df (pandas.DataFrame): A DataFrame containing the following columns:
            - "Users": User identifiers (grouping key).
            - "Time_sin": Sine transformation of time for circular representation.
            - "Time_cos": Cosine transformation of time for circular representation.

    Returns:
        tuple: A tuple containing:
            - numpy.ndarray: A 2D array where each element (i, j) represents the 
              cosine similarity between user `i` and user `j`.
            - pandas.DataFrame: A DataFrame with averaged sine and cosine time 
              values for each user. Columns:
                - "Users": User identifiers.
                - "Time_sin": Averaged sine values of activity times.
                - "Time_cos": Averaged cosine values of activity times.

    Example:
        Input DataFrame:
            Users  Time_sin  Time_cos
            User1   0.984808 -0.173648
            User1   0.923880 -0.382683
            User2   0.707107  0.707107
            User2   0.866025  0.500000

        Output:
            user_similarity_array:
                [[1.         0.8660254]
                 [0.8660254  1.        ]]
            
            df_time_vectors:
                Users  Time_sin  Time_cos
                User1  0.954344 -0.278166
                User2  0.786566  0.603553
    """
    # Group by users and compute the mean of sine and cosine transformations
    df_time_vectors = df.groupby("Users")[["Time_sin", "Time_cos"]].mean().reset_index()
    
    # Compute cosine similarity for the time vectors
    user_similarity_array = cosine_similarity(df_time_vectors[["Time_sin", "Time_cos"]])
    
    return user_similarity_array, df_time_vectors


def highest_similarity_pair(user_similarity_array, df_time_vectors):
    """
    Identifies the pair of users with the highest cosine similarity.

    This function creates a DataFrame to represent the cosine similarity between 
    users, excludes diagonal values (which represent self-similarity), and determines 
    the pair of users with the maximum similarity.

    Parameters:
        user_similarity_array (numpy.ndarray): A 2D array where each element (i, j) 
            represents the cosine similarity between user `i` and user `j`.
        df_time_vectors (pandas.DataFrame): A DataFrame containing:
            - "Users": User identifiers.

    Returns:
        tuple: A tuple containing:
            - str: Identifier of the first user in the most similar pair.
            - str: Identifier of the second user in the most similar pair.
            - float: The highest cosine similarity value between the two users.
    """
    user_similarity_df = pd.DataFrame(user_similarity_array, index=df_time_vectors["Users"],  columns=df_time_vectors["Users"])
    # For cosine similarity, we want the highest value (excluding the diagonal, since that will always be 1)
    mask = np.triu(np.ones(user_similarity_df.shape), k=1)  # Mask to exclude the diagonal
    masked_similarity = user_similarity_df.values * mask  # Apply the mask to remove diagonal
    # Find the index of the maximum similarity value
    max_sim_index = np.unravel_index(np.argmax(masked_similarity), masked_similarity.shape)
    user1 = user_similarity_df.index[max_sim_index[0]]
    user2 = user_similarity_df.columns[max_sim_index[1]]
    max_similarity_value = masked_similarity[max_sim_index]
    return user1, user2, max_similarity_value

def compute_highest_similarity_from_csv(file_path):
    """
    Computes the pair of users with the highest cosine similarity from a CSV file.

    This function checks if the provided file is a valid CSV, processes the data to 
    calculate sine and cosine representations of user times, computes cosine similarity 
    between users, and identifies the pair of users with the highest similarity.

    Parameters:
        file_path (str): The path to the CSV file containing user data with columns:
            - "Users": User identifiers.
            - "Times": Time values in "HH:MM:SS" format.

    Returns:
        tuple: A tuple containing:
            - str: Identifier of the first user in the most similar pair.
            - str: Identifier of the second user in the most similar pair.
            - float: The highest cosine similarity value between the two users.

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
        user_distance_array, df_time_vectors = obtain_cosine_similarity_array(df)
        user1, user2, max_similarity_value = highest_similarity_pair(user_distance_array, df_time_vectors)
        return user1, user2, max_similarity_value
    else:
        print("Innapropriate file")

