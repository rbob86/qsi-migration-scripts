# Qualifacts Migration Process

This repo contains custom-tailored scripts for migrating Qualifacts Looker customers from 150+ instances to 30. At a high-level, the process is as follows:

1. Generate .ini files to be used by lmanage capturator
2. Run lmanage capturator for selected instances
3. Detect duplicate slugs; if found, manually update
4. Combine customer settings/content based on proposed instance mapping
5. Run lmanage configurator to execute migration
6. Get customer mappings for folder id, viewer group id, and writer group id
7. Update owner for scheduled plans and alerts to original owner

> NOTE: Before execution, review `current-customer-instance-configuration-mapping.csv` to see which instances currently contain which customer accounts, and `proposed-customer-instance-mapping.csv` to see which customer accounts should end up together.  The latter is based on overall usage and peak time analysis. For overall usage analysis and alternative proposed mappings, see: https://docs.google.com/spreadsheets/d/18bgF59iOuMUrNLJmiuJreQRfI9YMy_BZYlVHm4CJh90/edit?gid=1194315819#gid=1194315819


![Migration Process](migration-process.jpg "Migration Process")

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

## Customer/Instance Mappings

The following files can help determine which customers/instances to download and migrate to:

- current-customer-instance-mapping.csv
- proposed-customer-instance-mapping.csv

Run the following to see a breakdown of customers from the proposed mapping and command output for steps 2, 4, 5 and 6:

```
python get_commands.py
```

This will result in an output like:

```
Instance No: 001
Customers: AAMHC DECNXNS2 ILSOSUB OCMACC PAARCMANOR WACHLDC CACMMHC EARTH GAIT MAVOLAM MTHFH OHBHCCH OHRFSCF SDLSSSD WILDR

Commands:
  Step 2
  python lmanage_parallel.py -i 013 024 046 050 061 092 103 117 120 123 127 134 137 151

  Step 4
  python consolidate_config_files.py --customers AAMHC DECNXNS2 ILSOSUB OCMACC PAARCMANOR WACHLDC CACMMHC EARTH GAIT MAVOLAM MTHFH OHBHCCH OHRFSCF SDLSSSD WILDR --instances qsi013 qsi024 qsi046 qsi050 qsi061 qsi092 qsi103 qsi117 qsi120 qsi123 qsi127 qsi134 qsi137 qsi151 --output-dir 001

  Step 5
  lmanage configurator --config-dir ../4-consolidate-config-files/output/001 --ini-file ini-files/clqsi001.ini

  Step 6
  python get_customer_mappings.py --ini-file ../5-lmanage-configurator/ini-files/clqsi001.ini --output-dir 001

  Step 7
  python update_content_owner.py --mapping ../4-consolidate-config-files/output/001/owner-mapping.json --ini-file ../5-lmanage-configurator/ini-files/clqsi001.ini

-----------------

Instance No: 002
Customers: AKACHMS DEMO INYTHOC OCNMH PAAUBER WACLRKC CAEXODUS CTCJR GARCVPL MAGADRA MIALLIANCE NJPREBH OHMATHP ORFAMSL PTHWY WAPOCCS

Commands:
  Step 2
  python lmanage_parallel.py -i 049 078 081 083 089 096 098 099 105 119 120 121 126 134 139 143

  Step 4
  python consolidate_config_files.py --customers AKACHMS DEMO INYTHOC OCNMH PAAUBER WACLRKC CAEXODUS CTCJR GARCVPL MAGADRA MIALLIANCE NJPREBH OHMATHP ORFAMSL PTHWY WAPOCCS --instances qsi049 qsi078 qsi081 qsi083 qsi089 qsi096 qsi098 qsi099 qsi105 qsi119 qsi120 qsi121 qsi126 qsi134 qsi139 qsi143 --output-dir 002

  Step 5
  lmanage configurator --config-dir ../4-consolidate-config-files/output/002 --ini-file ini-files/clqsi002.ini

  Step 6
  python get_customer_mappings.py --ini-file ../5-lmanage-configurator/ini-files/clqsi002.ini --output-dir 002

  Step 7
  python update_content_owner.py --mapping ../4-consolidate-config-files/output/002/owner-mapping.json --ini-file ../5-lmanage-configurator/ini-files/clqsi002.ini

...
```

Use these commands during the overall migration process for the desired instance.

## 1. Generating .ini files (optional)

> NOTE: This step is optional because `1-create-ini-files/` already contains .ini files for all instances.  However, if you want to use credentials for a new user, you would run this process.

**lmanage** requires a .ini file to authenticate to the Looker API. Since we are ultimately pulling content from 150+ instances, we need to run lmanage that many times, and authenticate that many times. Create a file called `looker-api-keys.csv` with columns looker_url,client_id,client_secret and store all instance API keys for the desired user. Then run the following to generate an ini file for each instance in the `ini-files/` folder:

```
cd 1-create-ini-files
python create_ini_files.py
```

## 2. Retrieving Customer Content & Settings

Navigate to the next directory:

```
cd 2-lmanage-capturator
```

### Run in Parallel

Using lmanage and the existing or newly created .ini files, capture content and settings in parallel by running:

```
python lmanage_parallel.py -i [list of ini filenames without extension]
```

Note that the -i argument takes a list of ini filenames without the .ini extension, for example:

```
python lmanage_parallel.py -i 001 166 032 044 123 009
```

This program will run `lmanage capturator` for the desired instances, in parallel, with 5 workers/threads (this can be changed by altering the MAX_WORKERS value, set appropriate value for your system).

After execution, saved content will be stored in `2-lmanage-capturator/config/config-[instance_no]`.

### Run for single instance

lmanage can also be run for a single individual instance with:

```
lmanage capturator \
  --config-dir ./config/config-001 \
  --ini-file 001.ini
```

Note the _--config-dir_ flag specifies where the YAML-based content and settings downloaded from the instance will be stored, and the _--ini-file_ flag references the appropriate ini file for authentication. In this case, we are targeting the qsi-001 url and credentials and storing its contents in a subfolder called `config-001`.

## 3. Detect Duplicate Slugs

Once all desired production content is saved, run:

```
cd 3-detect-duplicate-slugs
python detect_duplicate_slugs.py
```

This script will parse the subdirectories of `2-lmanage-capturator/config/` and alert if there are any duplicate dashboard slugs amongst all instance content.

- If none around found, proceed to step 4.
- If duplicates are found, update duplicated slugs with newly generated ones (use a password generator or similar to generate alphanumeric slugs of length 22).

## 4. Consolidate Config Files

Next we need to extract only the desired customer accounts from the various content.yaml and settings.yaml files generated from Step 2. In other words, based on the customer accounts you want to migrate to a target instance, this step will extract those accounts and consolidate them into a single pair of YAML files, which will serve as the basis for your migration. Using `proposed-customer-instance-mapping.csv` as a reference, run:

```
cd 4-consolidate-config-files

python consolidate_config_files.yaml \
  --customers [list of customers] \
  --instances [list of instances] \
  --output-dir [name of output dir]
```

- **--customers**: The customer accounts you want to consolidate
- **--instances**: The source files from which to extract content and settings
- **--output-dir**: The final location of the consolidated content and settings

Example:

```
python consolidate_config_files.py \
  --customers INDCTR CAMCC NJSTRES TNHEALTHCONNECT PIN \
  --instances qsi001 qsi002 qsi003 qsi004 qsi005 \
  --output-dir clqsi001
```

## 5. Migrate Data

Next we need to migrate the data produced by Step 4 to a target instance.

You'll need to first create a .ini file in `5-lmanage-configurator/ini-files/` with the credentials of the target instance, as such:

```
[Looker]
base_url=https://clqsi001.cloud.looker.com
client_id=[client_id]
client_secret=[client_secret]
verify_ssl=True
```

Then, run lmanage directly:

```
cd 5-lmanage-configurator

lmanage configurator \
  --config-dir [config_dir] \
  --ini-file [ini_file]
```

A concrete example: if you have a folder 001 with content.yaml and settings.yaml (created in step 4) and a .ini file with credentials for the target instance clqsi001, run:

```
lmanage configurator \
  --config-dir ../4-consolidate-config-files/output/001 \
  --ini-file ini-files/clqsi001.ini
```

lmanage configurator \
  --config-dir ../4-consolidate-config-files/output/166 \
  --ini-file ini-files/qsi166.ini

> NOTE: Ensure the use of an official service account for the ini-file credentials instead of a personal account, so saved content's metadata will not show the owner or created by as an employee.

## 6. Get Customer Group/Folder Mappings

For each migrated customer account we want to know the following of them:

- Name/Folder Name
- Folder ID
- Viewer Group ID
- Writer Group ID

For this, you can run the following:

```
cd 6-get-customer-mappings

python get_customer_mappings.py \
  --ini-file [ini file of target instance] \
  --output-dir [name of output subdirectory to store mapping csv]
```

For example:

```
python get_customer_mappings.py --ini-file ../5-lmanage-configurator/ini-files/qsi166.ini --output-dir 166
```

This will save a .csv similar to the following:

```
customer,instance,folder_id,viewer_group_id,writer_group_id
DEMO11,https://looker-166.qualifacts.org,3759,71,59
DEMO12,https://looker-166.qualifacts.org,3744,74,73
DEMO13,https://looker-166.qualifacts.org,3819,60,57
DEMO15,https://looker-166.qualifacts.org,3684,68,65
DEMO2,https://looker-166.qualifacts.org,3668,46,35
DEMO3,https://looker-166.qualifacts.org,3729,58,61
DEMO4,https://looker-166.qualifacts.org,3804,67,62
DEMO5,https://looker-166.qualifacts.org,3714,55,64
DEMO6,https://looker-166.qualifacts.org,3789,72,63
DEMO7,https://looker-166.qualifacts.org,3699,69,66
DEMO,https://looker-166.qualifacts.org,3774,56,70
```

This data can be used to populate associated values in carelogic.


## 7. Update Scheduled Plan/Alert Owner

Once content is migrated to a target instance, the owner of scheduled plans and alerts for dashboards needs to be updated on that instance.  Review the owner-mapping.json file generated from step 4 to confirm that the owners match their associated scheduled plans and alerts.  Then, run:

```
cd 7-update-content-owner

python update_content_owner.py \
  --mapping-dir [dir name containing owner-mapping.json from step #4] \
  --ini-file [ini_file]
```

Example, where the target instance is clqsi001:

```
python update_content_owner.py \
  --mapping ../4-consolidate-config-files/output/001/owner-mapping.json
  --ini-file ../5-lmanage-configurator/ini-files/clqsi001.ini
```
