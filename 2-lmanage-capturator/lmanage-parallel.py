import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

ini_files_dir = "../1-create-ini-files/ini-files"
ini_files = sorted(os.listdir(ini_files_dir))[0:5]


# Define a function to execute a single lmanage command
def run_lmanage(ini_file):
    config_num = ini_file.split(".")[0]
    config_dir = f"./config/config-{config_num}"
    ini_path = os.path.join(ini_files_dir, ini_file)
    command = [
        "lmanage",
        "capturator",
        "--config-dir",
        config_dir,
        "--ini-file",
        ini_path,
        "--force",
    ]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Print stdout and stderr in real-time
    for line in process.stdout:
        print(line, end="")

    for line in process.stderr:
        print(line, end="")

    process.wait()

    return f"Completed {ini_file}"


# Determine how many parallel tasks to run
# You can adjust the max_workers based on your system's capabilities
max_workers = 5  # Adjust this number based on your system

# Run the lmanage commands in parallel
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(run_lmanage, ini_file) for ini_file in ini_files]

    for future in as_completed(futures):
        result = future.result()
        print(result)

print("All tasks completed.")
