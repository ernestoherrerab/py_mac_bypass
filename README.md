A front end based on Flask has been added that allows the upload of a csv file.

The idea of this script is to add MAC addresses to a bypass list for guest users in ISE.
A CSV file is used as the input, this must be located in the csv_data directory on the same location where the script exists.

The CSV file should look like this:

MAC Address,Device Type,Description
AA:AA:AA:AA:AA:AA,Unknown,MAC number 1
BB:BB:BB:BB:BB:BB,Windows10-Workstation,MAC number 2
CC:CC:CC:CC:CC:CC,Windows11-Workstation,MAC number 3

Where the "Device Type" should use the exact name for the profile, otherwise it will be set to "Unknown".

The "Description" field is currently not in use.

An environment file called ".env" should also exist in the same directory where the script exists. The following must be added to that file:

ise_variable is either the IP address of ISE or the FQDN
The "Guest MAB ID" will be shared upon request.

URL_VAR = https://ise_variable:9060
GUEST_MAB_ID = The ID

Future enhancements:
- Authentication on the frontend.
- Possibility to add data manually too instead of CSV files.
