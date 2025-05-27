'''
Simple EDL Manager

Use Case: PalaoAlto or other FW when a local IIS server hosts EDL Lists.

Operation: Once configured, see README.md. Users can update and modify their EDL Lists with comments and a date
that represents the entry date. This program simply loads the file into a Pandas DF.  Removes records that are
more than X days old. It also validates that the specified IP address or Subnet is valid. If not, it removes
the invalid entry.

All executions or deletions from the lists are logged.
'''
import json
import logging
import sys
from datetime import timedelta
import ipaddress
import pandas as pd

with open('config.json', 'r', encoding='utf-8') as file:
    try:
        config_vars = json.load(file)
    except json.JSONDecodeError as e:
        print ('Failed to load config JSON: {e}')
        sys.exit(1)

source: str = config_vars['source']
edl_list_names: list = config_vars['edl_list_names']
EXP_DAYS: int = config_vars['expires']
OVERWRITE_ORIGINAL: bool = config_vars['overwrite_original']
ALWAYS_OVERWRITE: bool = config_vars['always_overwrite']

# Configure logging
logging.basicConfig(
    filename='ip-addr-mgr.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_dataframe_rows(df, current_file: str, log_type="INFO", additional_info: str="") -> None:
    """Logs each row of a Pandas DataFrame to a log file.

    Args:
        df (pd.DataFrame): The DataFrame to log.
        current_file (str): which file from the list we are on.
        log_type (str, optional): The log type (e.g., INFO, WARNING, ERROR). Defaults to "INFO".
        additional_info (str): for INFO logs
    """
    if df.empty:
        if additional_info == "":
            log_message = f"{log_type} File {current_file} no records processed."
        else:
            log_message = f"{additional_info}: File {current_file}."
        logging.info(log_message)

        return

    for index, row in df.iterrows():
        log_message = f"{log_type}: Row {index}: {row.to_dict()}"
        if log_type.upper() == "INFO":
            logging.info(log_message)
        elif log_type.upper() == "EXPIRED":
            logging.warning(log_message)
        elif log_type.upper() == "INVALID":
            logging.error(log_message)
        else:
            logging.info(log_message)

def is_valid_ip(ip_sub: str) -> bool:
    """
        test if an ip or subnet passed is a valid IP v4/v6 address of subnet
        return tru or false
    """

    try:
        ipaddress.ip_address(ip_sub)
        return True
    except ValueError:
        pass

    try:
        ipaddress.ip_network(ip_sub, strict=False)
        return True
    except ValueError:
        return False

def main()-> None:
    """
        _summary_main()


    """

    # support for multiple files
    for edl_list_name in edl_list_names:

        df_expired: pd.DataFrame = pd.DataFrame()
        df_active: pd.DataFrame = pd.DataFrame()
        df_invalid: pd.DataFrame = pd.DataFrame()

        log_dataframe_rows(pd.DataFrame, edl_list_name, "INFO", "start EDL processing")

        # Read the EDL list file
        df: pd.DataFrame = pd.read_csv(edl_list_name, sep="#", header=None, names=['IP Address', 'Comment', 'Date'])
       
        if df.empty:
            log_dataframe_rows(pd.DataFrame, edl_list_name, "INFO", "file is empty")
            continue

        # Convert the Date column to datetime format
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Clean up the Data
        df['IP Address'] = df['IP Address'].str.strip()

        try:
            df['Comment'] = df['Comment'].str.strip()
        except AttributeError:
            pass

        date_today = pd.Timestamp.today()
        cutoff_date = date_today - timedelta(days=EXP_DAYS)

        df_expired = df[(df['Date'] < cutoff_date)].copy()
        df_active = df[(df['Date'] > cutoff_date) | (df['Date'].isna())].copy()

        # Check IP Addresses
        df_active["Is IP Valid"] = df_active['IP Address'].apply(is_valid_ip)

        # Drop invalid IPs
        df_invalid = df_active[~df_active["Is IP Valid"]].copy()

        # All active IPs
        df_active = df_active[df_active["Is IP Valid"]].copy()

        # Add padding for IP Address and Comments
        df_active['Comment'] = df_active['Comment'].fillna('')
        df_active['IP Address'] = df_active['IP Address'] + " "
        df_active['Comment'] = " " + df_active['Comment'] + " "

        # No longer need column
        df_active = df_active.drop(columns =['Is IP Valid'])

        if df_expired.notnull:
            log_dataframe_rows(df_expired, edl_list_name, "EXPIRED")
        if df_invalid.notnull:
            log_dataframe_rows(df_invalid, edl_list_name, "INVALID")

        if not ALWAYS_OVERWRITE:
            if (df_expired.empty and df_invalid.empty):
                # No changes were made
                log_dataframe_rows(pd.DataFrame, edl_list_name, "INFO", "no changes were made")
        else:
            if OVERWRITE_ORIGINAL:
                exp_file = f'{source}{edl_list_name}'
            else:
                exp_file = f'{source}{edl_list_name}-X.txt'

            df_active.to_csv(exp_file, sep="#", index=False, header=False)
            log_dataframe_rows(pd.DataFrame, edl_list_name, "INFO", "end of run, file updated")

        print(df_active)

if __name__ == "__main__":
    main()
