import os.path
from NikGapps.Helper import FileOp, Constants

start_time = Constants.start_of_function()

folders_to_delete = ['10', '11', '12', '12.1', '13', 'Build', 'Releases', 'canary-release', 'release',
                     'nikgapps.github.io', 'TempPackages', 'overlays_SL', 'overlays_T']
for folder in folders_to_delete:
    if os.path.exists(Constants.pwd + Constants.dir_sep + folder):
        print("Deleting " + folder)
        FileOp.remove_dir(Constants.pwd + Constants.dir_sep + folder)
    else:
        print("Folder does not exist: " + folder)

Constants.end_of_function(start_time, "End of the program")
