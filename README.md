# A simple EDL Management tool

This simple tools allow the automation of an EDL (external Dynamic List) where users can manually populate multiple lists with ip address, subnets, comments and an entry date. The script will remove an entry once it expires, or if no expirey is specified. The entry is considered permanent and will remain. All updates and changes to files, are logged for review. Users can use these lists to manage an IP/subnet list for use in block or allow rules on any firewall that supports EDL's.  Hosting the EDL on an internal iis server or any other hmtl server is possible. Once installed, schedule a task to execute the script at whatever interval best fits your use case.

## Setup

edit the config.json file to suit your needs.

```json
{
    "edl_list_names": ["edl-list1.txt","edl-list2.txt","edl-list3.txt"],
    "source": "./",
    "expires": 30,
    "default_comment": "",
    "permanent_comment": "* permanent",
    "overwrite_original": false,
    "always_overwrite": true
}
```

### Information
*edl_list_name*: provide a list of text files you would like to monitor. Format of the file is as follows.
- 192.168.0.0/24 # comment # date_added
- 192.168.1.100 # # date_added
- 192.168.2.1/32 # comment
- 192.168.3.0/25

Each line should have an ip/subnet, a comment, and a date_added. However, the comment and date_added are optional as long as the # for a blank comment is set when adding the date_added field. Note, item 2 above. If no date is specified, the entry is considered permanent.

date_added is in the format of YYYY-MM-DD. eg 2025-02-22

*source*: enter the folder name where the txt files are located.

    "C:\\inetpub\\wwwroot"
    or
    "/var/www/html"

*expires*: the number of days to pass before the entry is removed.

*default_comment*: future
*permanent_comment*: future

*overwrite_original*: It's suggested to begin testing where the original
file is not overwritten. overwrite_original = "false". For production 
environments the objective is to update the original file when executed.

*always_overwrite*: In the case when there are no changes to the file,
the file is still overwritten.

### Execution
Run the script either manualy or via Windows/Linux scheduler at an interval that suites your needs.

