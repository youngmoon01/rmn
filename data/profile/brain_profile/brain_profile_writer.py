import json

ANSI_BGREEN = u"\u001b[32;1m"
ANSI_RESET = u"\u001b[0m"

RMN_HOME = '/home/youngmoon01/rmn/'
profile_export_path = RMN_HOME + 'data/profile/brain_profile/brain_profile.dat'

settings = {
    'brain_file_path': RMN_HOME + 'data/brain/brain.dat',
    'gradient_level': 8,
    'layer_depth': 10,

    # gradient-locality related
    'gradient_locality': 1,
    'gradient_weight': 0.9,

    # spatial-locality related
    'spatial_locality': 1,
    'spatial_weight': 0.9,

    # new cell weight range: [0, 1]
    'new_cell_weight': 0.5
}

dmp = json.dumps(settings)

profile_file = open(profile_export_path, 'w')
profile_file.write(dmp)
profile_file.close()

print(ANSI_BGREEN + 'New brain profile has been successfully written to target path' + ANSI_RESET)
