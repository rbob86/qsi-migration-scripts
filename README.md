# Qualifacts Migration Process

This repo contains custom-tailored scripts for migrating Qualifacts Looker customers from 150+ instances to 30. At a high-level, the process is as follows:

1. Generate .ini files to be used by lmanage capturator
2. Run lmanage capturator for all instances
3. Detect duplicate slugs, if found - manually update
4. Combine customer settings/content based on proposed instance mapping
5. Run lmanage configurator to execute migration
6. Update owner for scheduled plans and alerts to original owner

## 1. Generating .ini files

**lmanage** requires a .ini file to authenticate to the Looker API. Since we are pulling content from 150+ instances, we need to run lmanage that many times, and authenticate that many times. Create a file called `looker-api-keys.csv` with columns looker_url,client_id,client_secret and store all instance API keys for the desired user. Then run the following to generate an ini file for each instance in the `ini-files/` folder:

```
cd 1-create-ini-files
python create-ini-files.py
```

## 2. Retrieving Customer Content & Settings

Install lmanage:

```
pip install lmanage
```

Using lmanage and the newly created .ini files, capture content and settings once from each production instance, e.g.:

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
python consolidate-config-files.yaml
```

We'll need to run this once per target instance, so 30 times total. Store each output (content.yaml and settings.yaml) in a separate folder.

## 5. Migrate Data

If you have a folder qsi001 with content.yaml and settings.yaml and a .ini file with credentials for the target instance qsi001, run:

```
lmanage configurator --config-dir ./config/qsi001 --ini-file qsi001.ini
```

## 6. Update Scheduled Plan/Alert Owner
