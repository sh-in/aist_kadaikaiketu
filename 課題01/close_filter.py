import pandas as pd

# Read the CSV file
df = pd.read_csv('close_full_result.csv')

# Group by 'action', remove duplicates in 'objlabel', and get up to 10 'objlabel' for each action
result = df.groupby('action')['objlabel'].apply(lambda x: x.drop_duplicates().head(10)).reset_index()

# Print the result
print(result)

# Save the result to a CSV file
result.to_csv('close_filtered_result.csv', index=False)