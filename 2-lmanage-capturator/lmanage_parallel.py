import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging


logging.basicConfig(level=logging.INFO)


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

    logging.info(f"Running command: {' '.join(command)}")

    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Use communicate to get the output
        stdout, stderr = process.communicate()

        logging.info(stdout)
        logging.error(stderr)

        if process.returncode != 0:
            logging.error(f"Error running {ini_file}: {stderr}")

    except Exception as e:
        logging.error(f"Exception occurred for {ini_file}: {e}")

    return f"Completed {ini_file}"


# Determine how many parallel tasks to run
# You can adjust the max_workers based on your system's capabilities
MAX_WORKERS = 5  # Adjust this number based on your system

parser = argparse.ArgumentParser(
    description="Capture [num_instances] instances starting at number [offset]."
)
parser.add_argument(
    "--ini-files",
    "-i",
    nargs="+",
    required=True,
    help="List of .ini files to capture.",
)
args = parser.parse_args()

ini_filenames = [f"{i}.ini" for i in args.ini_files]

ini_files_dir = "../1-create-ini-files/ini-files"
all_ini_files = os.listdir(ini_files_dir)
ini_files_filtered = [i for i in all_ini_files if i in ini_filenames]

# Run the lmanage commands in parallel
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [
        executor.submit(run_lmanage, ini_file) for ini_file in ini_files_filtered
    ]

    for future in as_completed(futures):
        result = future.result()
        print(result)

print("All tasks completed.")
