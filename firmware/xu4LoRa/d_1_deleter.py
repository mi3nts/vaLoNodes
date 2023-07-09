import os
import sys
import shutil
import datetime

def main():
    dirPath = os.path.normpath("/home/teamlary/mintsDataTmp")
    print("Deleting going thorugh folder: "+ dirPath)
    for filename in os.listdir(dirPath):
        file_path = os.path.join(dirPath, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                print("Deleting: "+ file_path)
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                print("Deleting: "+ file_path)
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

        
    dirPath = os.path.normpath("/home/teamlary/mintsDataJson")
    print("Deleting going thorugh folder: "+ dirPath)
    for filename in os.listdir(dirPath):
        file_path = os.path.join(dirPath, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                print("Deleting: "+ file_path)
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                print("Deleting: "+ file_path)
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
                
if __name__ == '__main__':
    main()