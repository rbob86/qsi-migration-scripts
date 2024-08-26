# Example End-to-end Walkthrough

This is a full end-to-end walkthrough of the downloading of content and settings from all "demo" accounts and migrating it to https://qsi166.cloud.looker.com.  You can see video walkthroughs of each step at: https://drive.google.com/corp/drive/folders/1lJR_jV8R_sIGOwugGdnfsyL0BlGtq88f?resourcekey=0-3CcJIrv925JGjISJjysihg.

> NOTE: The customer account to instance mapping can be seen in `current-customer-instance-mapping.csv`.

## Set up Python virtual environment:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 1. Create .ini files

_No action needed._

## 2. Capture

```
cd 2-lmanage-capturator
python lmanage_parallel.py -i 011 073 074 076 077 086 087 088 089 090 110
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
  --customers DEMO DEMO2 DEMO3 DEMO4 DEMO5 DEMO6 DEMO7 DEMO11 DEMO12 DEMO13 DEMO15 \
  --instances qsi011 qsi073 qsi074 qsi076 qsi077 qsi086 qsi087 qsi088 qsi089 qsi090 qsi110 \
  --output-dir 166
```

This will store consolidated output and owner-mapping.json in `4-consolidate-config-files/output/166`

## 5. Migrate

Create a `qsi166.ini` file in `5-lmanage-configurator/ini-files`:

```
[Looker]
base_url=https://qsi166.cloud.looker.com
client_id=K5T8bZxNrHHysksMXdjd
client_secret=cgypSM5cYDXgpndKRpCRY9Nv
verify_ssl=True
```

Then, run:

```
cd ../5-lmanage-configurator

lmanage configurator \
  --config-dir ../4-consolidate-config-files/output/166 \
  --ini-file ini-files/qsi166.ini
```

## 6. Get customer folder/group mappings

```
cd ../6-get-customer-mappings

python get_customer_mappings.py --ini-file ../5-lmanage-configurator/ini-files/qsi166.ini --output-dir 166
```

This will output a .csv containing all customer accounts, their respective folder id, and their respective viewer and writer group ids, like so:

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

## 7. Update plan/alert owners

```
cd ../7-update-content-owner

python update_content_owner.py \
  --mapping ../4-consolidate-config-files/output/166/owner-mapping.json \
  --ini-file ../5-lmanage-configurator/ini-files/qsi166.ini
```