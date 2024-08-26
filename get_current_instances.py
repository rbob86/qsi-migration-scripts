import csv
import re
from collections import defaultdict

# Load the looker_url CSV into a dictionary where the key is the customer and the value is the looker URL number
customer_to_url = defaultdict(set)  # Using a set to ensure uniqueness
with open('current-customer-instance-mapping.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        customers = row['customers'].split(',')
        url_number = re.search(r'qsi(\d+)', row['looker_url']).group(1)
        for customer in customers:
            customer_to_url[customer.strip()].add(url_number)  # Add to set for uniqueness

# Function to find the current instances for each customer in a given row
def find_current_instances(instance_row):
    instances = set()  # Use a set to ensure uniqueness across all customers in the row
    customers = instance_row['customers'].split(',')
    for customer in customers:
        customer = customer.strip()
        if customer in customer_to_url:
            instances.update(customer_to_url[customer])
    return sorted(instances)  # Return a sorted list of unique numbers

# Load the instance CSV and print the current instances for each row
with open('proposed-customer-instance-mapping.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        instance_no = f"{int(row['instance_no']):03d}"
        current_instances = find_current_instances(row)
        customers = row['customers'].replace(',', '')
        qsi_instances = [f"qsi{i}" for i in current_instances]

        print(f"Instance No: {instance_no}")
        print(f"Customers: {customers}")
        print(f"Step 2 Command: python lmanage_parallel.py -i {' '.join(current_instances)}")
        print(f"Step 4 Command: python consolidate_config_files.py --customers {customers} --instances {' '.join(qsi_instances)} --output-dir {instance_no}\n")
