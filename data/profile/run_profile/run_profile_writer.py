import json

ANSI_BGREEN = u"\u001b[32;1m"
ANSI_RESET = u"\u001b[0m"

RMN_HOME = '/home/youngmoon01/rmn/'
profile_export_path = 'data/profile/run_profile/run_profile.dat'

settings = {
    'image_directory_path': RMN_HOME + 'data/training/images/',
    'image_label_path': RMN_HOME + 'data/training/labels.dat',
    'target_range': (1, 60000)
}

dmp = json.dumps(settings)

profile_file = open(RMN_HOME + profile_export_path, 'w')
profile_file.write(dmp)
profile_file.close()

print(ANSI_BGREEN + 'New profile has been successfully written to target path' + ANSI_RESET)
