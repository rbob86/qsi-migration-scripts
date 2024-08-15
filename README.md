# Qualifacts Migration Process

This repo contains custom-tailored scripts for migrating Qualifacts Looker customers from 150+ instances to 30. At a high-level, the process is as follows:

1. Generate .ini files to be used by lmanage capturator
2. Run lmanage capturator for all instances
3. Detect duplicate slugs, if found - manually update
4. Combine customer settings/content based on proposed instance mapping
5. Run lmanage configurator to execute migration
6. Update owner for scheduled plans and alerts to original owner

## Installation

Create and activate the virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```
pip install -r requirements.txt
```

If **lmanage** is not accessible via the command line:

```
pip install lmanage
```

## 1. Generating .ini files (optional)

**lmanage** requires a .ini file to authenticate to the Looker API. Since we are pulling content from 150+ instances, we need to run lmanage that many times, and authenticate that many times. Create a file called `looker-api-keys.csv` with columns looker_url,client_id,client_secret and store all instance API keys for the desired user. Then run the following to generate an ini file for each instance in the `ini-files/` folder:

```
cd 1-create-ini-files
python create-ini-files.py
```

## 2. Retrieving Customer Content & Settings

Navigate to the next directory:

```
cd 2-lmanage-capturator
```

### Run in Parallel

Using lmanage and the existing or newly created .ini files, capture content and settings in parallel by running:

```
python lmanage-parallel.py -i [list of ini filenames without extension]
```

Note the -i argument takes a list of ini filenames without the .ini extension, for example:

```
python lmanage-parallel.py -i 001 166 032 044 123 009
```

This program will run `lmanage capturator` for the desired instances, in parallel, with 5 workers/threads (this can be changed by altering the MAX_WORKERS value, set appropriate value for your system).

After execution, saved content will be stored in `2-lmanage-capturator/config/config-[instance_no]`.

### Run for single instance

lmanage can also be run for a single individual instance with:

```
lmanage capturator --config-dir ./config/config-001 --ini-file 001.ini
```

Note the _--config-dir_ flag specifies where the YAML-based content and settings will be stored, and the _--ini-file_ flag references the appropriate ini file for authentication. In this case, we are targeting the qsi-001 url and credentials and storing its contents in a subfolder called `config-001`.

## 3. Detect Duplicate Slugs

Once all production content is saved, move all content.yaml files to `3-detect-duplicate-slugs/content-files` and run:

```
cd 3-detect-duplicate-slugs
python detect-duplicate-slugs.py
```

This script will alert if there are any duplicate dashboard slugs amongst all instance content. If none around found, proceed to step 4. If duplicates are found, update duplicated slugs with newly generated ones (use a password generator or similar to generate alphanumeric slugs of length 22).

## 4. Consolidate Config Files

Next we need to rearrange the content of the content.yaml and config.yaml files generated from each instance in a way that represents how the target instances will look. Using `proposed-customer-instance-mapping.csv` as a reference, run:

```
cd 4-consolidate-config-files

python consolidate-config-files.yaml --customers [list of customers] --instances [list of instances] --output-dir [name of output dir]
```

This script will consolidate customer settings and content, for customers specified by --customers, across multiple instance config files, specified by --instances, into a single set of config files, stored in --output-dir. And example of this command would be:

```
python consolidate_config_files.py --customers INDCTR CAMCC NJSTRES TNHEALTHCONNECT PIN --instances qsi001 qsi002 qsi003 qsi004 qsi005 --output-dir 001
```

We'll need to run this once per target instance, so 30 times total. Store each consolidate config (content.yaml and settings.yaml) in a separate output folder.

## 5. Migrate Data

Next we need to migrate the data produced by Step 4 to a target instance:

```
lmanage configurator --config-dir [config_dir] --ini-file [ini_file]
```

A concrete example: if you have a folder qsi001 with content.yaml and settings.yaml and a .ini file with credentials for the target instance qsi001, run:

```
lmanage configurator --config-dir ./config/qsi001 --ini-file qsi001.ini
```

> NOTE: Ensure the use of an official service account for the ini-file credentials instead of a personal account, so saved content's metadata will not show the owner or created by as an employee.

## 6. Update Scheduled Plan/Alert Owner

Once content is migrated to a target instance, the owner of scheduled plans and alerts for dashboards needs to be updated on that instance.
