import csv
from pymongo import MongoClient
import certifi

# Connect to your cloud database
connection_string = "mongodb+srv://thesis_admin:CQvw7ESoyGx1k3b8@dynamicmaze.bptjs3z.mongodb.net/?appName=DynamicMaze"
client = MongoClient(connection_string, tlsCAFile=certifi.where())
db = client['thesis_database']
collection = db['simulation_results']

print("Fetching data from the cloud...")
records = list(collection.find({}))

# Create the CSV file
filename = "thesis_data.csv"

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the Header row (MATLAB will use these as variable names)
    writer.writerow(['run_id', 'date', 'bfs_nodes', 'bfs_time_ms', 'bfs_path', 'bfs_mem_kb', 'dfs_nodes', 'dfs_time_ms', 'dfs_path', 'dfs_mem_kb'])
    
    # Loop through your cloud data and write each row
    for data in records:
        writer.writerow([
            data.get('id', ''),
            data.get('date', ''),
            data['bfs']['nodes'],
            data['bfs']['time_ms'],
            data['bfs']['path'],
            data['bfs']['mem_kb'],
            data['dfs']['nodes'],
            data['dfs']['time_ms'],
            data['dfs']['path'],
            data['dfs']['mem_kb']
        ])

print(f"Success! Your data has been exported to {filename}. You can now import this into MATLAB!")