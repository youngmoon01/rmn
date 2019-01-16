import json

ANSI_BGREEN = u"\u001b[32;1m"
ANSI_RESET = u"\u001b[0m"

RMN_HOME = '/home/youngmoon01/rmn/'
profile_export_path = RMN_HOME + 'data/profile/brain_profile/brain_profile.dat'

settings = {
    'brain_file_path': RMN_HOME + 'data/brain/brain.dat',
    'gradient_level': 8,
    'f_width': 30,
    'f_height': 30,

    'spatial_weight': 1.0,
    'gradient_weight': 1.0
}

dmp = json.dumps(settings)

profile_file = open(profile_export_path, 'w')
profile_file.write(dmp)
profile_file.close()

print(ANSI_BGREEN + 'New brain profile has been successfully written to target path' + ANSI_RESET)
