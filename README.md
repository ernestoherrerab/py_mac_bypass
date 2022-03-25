A front end based on Flask has been added that allows the upload/deletion of a csv file or manual data input.

The idea of this script is to add MAC addresses to a bypass list for guest users in ISE.
A CSV file or manual input is used as the input.

The format of the CSV is shown on the File Upload Page.

An environment file called ".env" should also exist in the same directory where the script exists. The following must be added to that file:

ise_variable is either the IP address of ISE or the FQDN
The "Guest MAB ID" will be shared upon request.

URL_VAR = https://ise_variable:9060
GUEST_MAB_ID = The ID
SECRET_KEY = A random secret 
FLASK_SERVER = x.x.x.x 
DEBUG_MODE = True or False

