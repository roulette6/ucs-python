# UCS Python SDK scripts
This repo contains scripts for performing tasks with the UCS Manager Python SDK `ucsmsdk` module.

## Scrips
* __get_vlan_groups_in_vnic_templ.py:__ Displays a list of all VLAN groups and their member VLANs and a list of vNIC templates and the VLAN group they use.
* __backup_ucs.py:__ Back up the full UCS config and save to current dir.
* __delete_pin_groups.py:__ Removes pin groups from vNIC templates and then deletes the pin groups.
* __restore_-_ucs.py:__ Loads blank config to UCS-PE
* __ucspe_backup_blank.xml:__ Blank UCS-PE config
* __ucspe_backup_lan.xml:__ UCS-PE config with LAN objects
  - VLANs
  - VLAN groups
  - Pin groups
  - vNIC templates referencing VLAN groups and pin groups
  - LAN connectivity policies referencing vNIC templates
  - readonly user `ucsro` with password `ucsro`
