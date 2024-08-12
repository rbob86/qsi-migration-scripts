import csv

# File name of the CSV file to be read
csv_file = "looker-api-keys.csv"

# Read the CSV file
with open(csv_file, mode="r") as file:
    reader = csv.DictReader(file)

    # Initialize a counter for file naming
    file_counter = 1

    # Iterate over each row in the CSV
    for row in reader:
        # Create the .ini file content
        ini_content = f"""[Looker]
base_url={row['looker_url']}
client_id={row['client_id']}
client_secret={row['client_secret']}
verify_ssl=True
"""
        # Define the filename (e.g., 001.ini, 002.ini, ...)
        ini_filename = f"ini-files/{file_counter:03}.ini"

        # Write the content to the .ini file
        with open(ini_filename, mode="w") as ini_file:
            ini_file.write(ini_content)

        # Increment the counter for the next file
        file_counter += 1

print("INI files created successfully.")
