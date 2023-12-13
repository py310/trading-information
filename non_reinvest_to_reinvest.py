import pandas as pd

def read_csv(file_path):
    try:
        # Attempt to read the CSV file into a pandas DataFrame
        return pd.read_csv(file_path)
    except FileNotFoundError:
        # Handle the case where the file is not found, print an error message, and return None
        print(f"Error: File '{file_path}' not found.")
        return None

def calculate_returns(df, rebalance_months):

    # Check if the required columns ('equity' and 'time') are present in the DataFrame
    if 'equity' not in df.columns or 'time' not in df.columns:
        raise ValueError("Required columns ('equity' and 'time') not found in the DataFrame.")

    # Calculate the percentage change of the 'equity' column and fill NaN values with 0
    df['pnl'] = df['equity'].pct_change().fillna(0)

    # Extract the month from the 'time' column
    df['month'] = pd.to_datetime(df['time']).dt.month
    
    # Initialize additional columns
    df['multiplier'] = 0
    df['pnl_reinvest'] = 0
    multiplier = 1
    cumulative_result = 0

    # Iterate through the DataFrame rows
    for i in df.index:

        # Check if the current month is in the rebalance_months list
        # and if the index is not 0 and the previous month is not in rebalance_months
        if df.loc[i,'month'] in rebalance_months and i != 0 and df.loc[i-1,'month'] not in rebalance_months:
            # Update the 'multiplier' variable
            multiplier = cumulative_result + 1

        # Calculate today's result and update the 'cumulative_result' variable
        today_result = df.loc[i,'pnl'] * multiplier
        cumulative_result += today_result

        # Update specific columns in the DataFrame
        df.loc[i, 'multiplier'] = multiplier
        df.loc[i, 'pnl_reinvest'] = today_result
    
    # Calculate the 'equity_reinvest'
    df['equity_reinvest'] = (df['pnl_reinvest'] + 1).cumprod()

    # Remove the 'month' column
    del df['month']
    return df

def save_results(df, output_filename):
    # Save the results to a CSV file with a semicolon as the separator and without index
    df.to_csv(output_filename, sep=';', index=False)

def main():
    # Input and output filenames
    input_filename = 'my_equity.csv'
    output_filename = f"reinvest_{input_filename}"
    
    # List of months where rebalance operations occur
    rebalance_months = [1]  # Example: [1, 4, 7, 10]

    # Read the CSV file into a DataFrame
    df = read_csv(input_filename)

    # Check if the DataFrame is not None (file was successfully read)
    if df is not None:
        # Perform calculations on the DataFrame
        df = calculate_returns(df, rebalance_months)
        
        # Save the results to a new CSV file
        save_results(df, output_filename)
        
        # Print the final DataFrame
        print(df)


if __name__ == "__main__":
    # Execute the main function if the script is run directly
    main()