import os.path
from NikGapps.Helper import FileOp, C

start_time = C.start_of_function()

folders_to_delete = ['10', '11', '12', '12.1', '13', 'Releases', 'canary-release', 'release',
                     'nikgapps.github.io', 'TempPackages', 'overlays_SL', 'overlays_T']
for folder in folders_to_delete:
    if os.path.exists(C.pwd + C.dir_sep + folder):
        print("Deleting " + folder)
        FileOp.remove_dir(C.pwd + C.dir_sep + folder)
    else:
        print("Folder does not exist: " + folder)

C.end_of_function(start_time, "End of the program")
