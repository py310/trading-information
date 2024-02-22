import pandas as pd

def stochastic(df: pd.DataFrame, k_period: int, d_period: int, smooth_k: int, append: bool = True) -> pd.DataFrame:
    """
    Calculates the stochastic oscillator for a given DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the OHLC data.
        k_period (int): The period for calculating the %K line.
        d_period (int): The period for calculating the %D line.
        smooth_k (int): The period for smoothing the %K line.
        append (bool, optional): Whether or not to append the %K and %D columns to the original DataFrame (default: True).

    Returns:
        pd.DataFrame: The original DataFrame with %K and %D columns added or just columns %K and %D.
    """
    # Calculate the rolling maximum and minimum of the High and Low prices over a period of k_period days.
    df['n_high'] = df['High'].rolling(k_period).max()
    df['n_low']  = df['Low'].rolling(k_period).min()

    # Calculate the %K line using the rolling maximum and minimum values and smooth it over a period of smooth_k days.
    df['K'] = ((df['Close'] - df['n_low']) * 100 / (df['n_high'] - df['n_low'])).rolling(smooth_k).mean()

    # Calculate the %D line by smoothing the %K line over a period of d_period days.
    df['D'] = df['K'].rolling(d_period).mean()

    # Drop the intermediate columns used to calculate %K and %D.
    df.drop(['n_high', 'n_low'], axis=1, inplace=True)

    # Fill any missing values using forward fill.
    df.fillna(method='ffill', inplace=True)
    
    # If append=False, only return the %K and %D columns.
    if not append:
        df = df[['K', 'D']]
    
    return df

def donchian(df: pd.DataFrame, period: int, offset: int = 0, append: bool = True) -> pd.DataFrame:
    """
    Calculates the Donchian Channel for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the OHLC data.
        period (int): The period for calculating the Donchian Channel.
        offset (int, optional): Offset for calculating the Donchian Channel (default: 0).
        append (bool, optional): Whether or not to append the Upper, Lower, and Middle columns to the original DataFrame (default: True).

    Returns:
        pd.DataFrame: The original DataFrame with Upper, Lower, and Middle columns added or just columns Upper, Lower, and Middle.
    """
    # Calculate the rolling maximum and minimum of the High and Low prices over a period of 'period' days.
    df['Upper'] = df['High'].rolling(period).max().shift(offset)
    df['Lower'] = df['Low'].rolling(period).min().shift(offset)

    # Calculate the Middle Line as the average of Upper and Lower.
    df['Middle'] = (df['Upper'] + df['Lower']) / 2

    # Drop rows with NaN values.
    df.dropna(inplace=True)

    # If append=False, only return the Upper, Lower, and Middle columns.
    if not append:
        df = df[['Upper', 'Lower', 'Middle']]

    return df

def atr(df: pd.DataFrame, period: int, relative=True, append: bool = True) -> pd.DataFrame:
    """
    Calculates the Average True Range (ATR) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the OHLC data.
        period (int): The period for calculating the ATR.
        relative (bool, optional): Whether to calculate ATR as an absolute or relative value (default: True).
        append (bool, optional): Whether or not to append the ATR column to the original DataFrame (default: True).

    Returns:
        pd.DataFrame: The original DataFrame with ATR column added or just the ATR column.
    """
    # Calculate the True Range (TR) which is the maximum of the following:
    # 1. High - Low
    # 2. Absolute value of High - Close (previous)
    # 3. Absolute value of Low - Close (previous)
    df['HL'] = df['High'] - df['Low']
    df['HC'] = abs(df['High'] - df['Close'].shift(1))
    df['LC'] = abs(df['Low'] - df['Close'].shift(1))

    # Calculate True Range (TR)
    df['TR'] = df[['HL', 'HC', 'LC']].max(axis=1)

    # Calculate the Average True Range (ATR) over the specified period.
    if relative:
        # Calculate ATR as a percentage of the Close price.
        df['ATR'] = (df['TR'].rolling(period).mean() / df['Close']) * 100
    else:
        # Calculate ATR as the simple average of TR.
        df['ATR'] = df['TR'].rolling(period).mean()

    # Drop the intermediate columns used to calculate TR.
    df.drop(['HL', 'HC', 'LC', 'TR'], axis=1, inplace=True)

    # Drop rows with NaN values.
    df.dropna(inplace=True)

    # If append=False, only return the ATR column.
    if not append:
        df = df[['ATR']]

    return df

def deciles(df: pd.DataFrame, column: str, append: bool = True) -> pd.DataFrame:
    """
    Calculates deciles for a specific column in a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The column for which deciles are calculated.
        append (bool, optional): Whether or not to append the decile columns to the original DataFrame (default: True).

    Returns:
        pd.DataFrame: The original DataFrame with decile columns added or just the decile columns.
    """
    # Calculate deciles using the pandas qcut function.
    df['Decile'] = pd.qcut(df[column], q=10, labels=False, duplicates='drop')

    # If append=False, only return the Decile column.
    if not append:
        df = df[['Decile']]

    return df

def bollinger_bands(df: pd.DataFrame, window: int, num_std_dev: int = 2, append: bool = True) -> pd.DataFrame:
    """
    Calculates Bollinger Bands for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the OHLC data.
        window (int): The window size for calculating the moving average.
        num_std_dev (int, optional): The number of standard deviations for the Bollinger Bands (default: 2).
        append (bool, optional): Whether or not to append the Bollinger Bands columns to the original DataFrame (default: True).

    Returns:
        pd.DataFrame: The original DataFrame with UpperBollinger, LowerBollinger, and MiddleBollinger columns added or just these columns.
    """
    # Calculate the rolling mean and standard deviation of the Close prices.
    df['MiddleBollinger'] = df['Close'].rolling(window).mean()
    df['UpperBollinger'] = df['MiddleBollinger'] + num_std_dev * df['Close'].rolling(window).std()
    df['LowerBollinger'] = df['MiddleBollinger'] - num_std_dev * df['Close'].rolling(window).std()

    # Drop rows with NaN values.
    df.dropna(inplace=True)

    # If append=False, only return the Bollinger Bands columns.
    if not append:
        df = df[['UpperBollinger', 'LowerBollinger', 'MiddleBollinger']]

    return df