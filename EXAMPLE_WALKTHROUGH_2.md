# Example End-to-end Walkthrough

This is a full end-to-end walkthrough of the downloading of content and settings from all proposed customer accounts for clqsi001 and migrating it to https://clqsi001.cloud.looker.com.

> NOTE: The customer account to instance mapping can be seen in `current-customer-instance-mapping.csv`.

## Set up Python virtual environment:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Get commands dynamically

Run:

```
python get_commands.py
```

To get a list of commands generated for you for all of the proposed instance configurations.  In this case, you'll want to copy the ones for "Instance No: 001":

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
  ```

## 1. Create .ini files

_No action needed._

## 2. Capture

```
cd 2-lmanage-capturator
python lmanage_parallel.py -i 013 024 046 050 061 092 103 117 120 123 127 134 137 151
```

This will store instance output in `2-lmanage-capturator/config/`.

## 3. Detect duplicate slugs

```
cd ../3-detect-duplicate-slugs
python detect_duplicate_slugs.py
```

_No duplicates found._

## 4. Consolidate

```
cd ../4-consolidate-config-files

python consolidate_config_files.py \
  --customers AAMHC DECNXNS2 ILSOSUB OCMACC PAARCMANOR WACHLDC CACMMHC EARTH GAIT MAVOLAM MTHFH OHBHCCH OHRFSCF SDLSSSD WILDR \
  --instances qsi013 qsi024 qsi046 qsi050 qsi061 qsi092 qsi103 qsi117 qsi120 qsi123 qsi127 qsi134 qsi137 qsi151 \
  --output-dir 001
```

This will store consolidated output and owner-mapping.json in `4-consolidate-config-files/output/001`

## 5. Migrate

Create a `clqsi001.ini` file in `5-lmanage-configurator/ini-files`:

```
[Looker]
base_url=https://clqsi001.cloud.looker.com
client_id=[client_id]
client_secret=[client_secret]
verify_ssl=True
```

Then, run:

```
cd ../5-lmanage-configurator

lmanage configurator \
  --config-dir ../4-consolidate-config-files/output/001 \
  --ini-file ini-files/clqsi001.ini
```

## 6. Get customer folder/group mappings

```
cd ../6-get-customer-mappings

python get_customer_mappings.py --ini-file ../5-lmanage-configurator/ini-files/clqsi001.ini --output-dir 001
```

This will output a .csv containing all customer accounts, their respective folder id, and their respective viewer and writer group ids.

## 7. Update plan/alert owners

```
cd ../7-update-content-owner

python update_content_owner.py \
  --mapping ../4-consolidate-config-files/output/001/owner-mapping.json \
  --ini-file ../5-lmanage-configurator/ini-files/clqsi001.ini
```