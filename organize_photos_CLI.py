import os
import sys
import string
from collections import namedtuple

import exiftool
import time

map_create_date_dict = {
    '.jpg': ['EXIF:CreateDate', 'DateTimeOriginal'],
    '.mov': ['QuickTime:CreateDate'],
    '.mp4': ['QuickTime:CreateDate'],
}

directories_to_organize2 = {
    'Z:/Zdjecia/Adelina/Do segregacji/': 'Z:/Zdjecia/Adelina',
    'Z:/Zdjecia/Agnieszka/Do segregacji/': 'Z:/Zdjecia/Agnieszka',
    'Z:/Zdjecia/Bernard/Do segregacji/': 'Z:/Zdjecia/Bernard',
    'Z:/Zdjecia/Damian/Do segregacji/': 'Z:/Zdjecia/Damian',
    'Z:/Zdjecia/Joanna/Do segregacji/': 'Z:/Zdjecia/Joanna',
    'Z:/Zdjecia/Natalia/Do segregacji/': 'Z:/Zdjecia/Natalia',
    'Z:/Zdjecia/Piotrek/Do segregacji/': 'Z:/Zdjecia/Piotrek',
    'Z:/Zdjecia/Rodzice/Do segregacji/': 'Z:/Zdjecia/Rodzice',
    'Z:/Zdjecia/Wspolne/Do segregacji/': 'Z:/Zdjecia/Wspolne'
}

directories_to_organize = {
    '/mnt/Z/Zdjecia/Adelina/Do segregacji/': '/mnt/Z/Zdjecia/Adelina',
    '/mnt/Z/Zdjecia/Agnieszka/Do segregacji/': '/mnt/Z/Zdjecia/Agnieszka',
    '/mnt/Z/Zdjecia/Bernard/Do segregacji/': '/mnt/Z/Zdjecia/Bernard',
    '/mnt/Z/Zdjecia/Damian/Do segregacji/': '/mnt/Z/Zdjecia/Damian',
    '/mnt/Z/Zdjecia/Joanna/Do segregacji/': '/mnt/Z/Zdjecia/Joanna',
    '/mnt/Z/Zdjecia/Natalia/Do segregacji/': '/mnt/Z/Zdjecia/Natalia',
    '/mnt/Z/Zdjecia/Piotrek/Do segregacji/': '/mnt/Z/Zdjecia/Piotrek',
    '/mnt/Z/Zdjecia/Rodzice/Do segregacji/': '/mnt/Z/Zdjecia/Rodzice',
    '/mnt/Z/Zdjecia/Wspolne/Do segregacji/': '/mnt/Z/Zdjecia/Wspolne'
}

input_path = './Input/'
output_path = './Output/'
initial_input_path = ''
LOG_FILE = 'log.txt'
et = None

def organize_files_in_output_folder(input_folder_path, root_output_path='', counter=[0]):
    # if not root_output:
    #     root_output = input_folder_path
    if not root_output_path:
        root_output_path = input_folder_path

    if os.path.isdir(input_folder_path) and not input_folder_path.endswith('/'):
        input_folder_path += '/'
    input_folder = os.listdir(input_folder_path)
    for item_name in input_folder:
        # print('item name={}'.format(item_name))
        if os.path.isdir(input_folder_path + item_name):
            organize_files_in_output_folder(input_folder_path + item_name, root_output_path, counter)
        else:
            file_path = input_folder_path + item_name
            # print('file_path={}'.format(file_path))
            new_directory = get_new_directory_based_on_date_taken(file_path, root_output_path)
            if new_directory:  # image or video 'date taken' available
                new_filepath = new_directory + item_name
                if os.path.isfile(new_filepath):
                    if os.stat(file_path).st_size == os.stat(new_filepath).st_size:  # duplicate file (same size)
                        os.remove(file_path)
                        print('File: {} has been removed since it is duplicate. '
                              'Comparison based on file size.'.format(file_path))
                        continue
                    else:  # same file name but not direct duplicate
                        new_directory = root_output_path + '/Segregacja Reczna/Duplikaty/' \
                                        + input_folder_path.replace(root_output_path, '/')
            else:  # missing metadata
                new_directory = root_output_path + '/Segregacja Reczna/Brak Danych/' \
                                + input_folder_path.replace(root_output_path, '/')

            ensure_folder_exist(new_directory)
            new_filepath = new_directory + item_name

            # bloc try/exeption can be cleaned up
            try:
                os.rename(file_path, new_filepath)
                print('From: {}, To: {}'.format(file_path, new_filepath))
            except FileExistsError as e:
                # print('Problem renaming file {}, error: {}'.format(file_path, e))
                if os.stat(file_path).st_size == os.stat(new_filepath).st_size:
                    os.remove(file_path)
                    print('File: {} has been removed since it is duplicate. '
                          'Comparison based on file size.'.format(file_path))
                else:
                    print("File with the same name exist in output folder but its not duplicate (size comparision). "
                          "Output file: {}".format(file_path, new_filepath))
            except Exception as exp:
                print(str(exp))
                e = sys.exc_info()[0]
                print(e)

            counter[0] = counter[0] + 1
    return counter


def get_new_directory_based_on_date_taken(input_path='', output_folder=''):
    if not input_path:
        return None
    else:
        output_folder_has_slash_on_end = output_folder.endswith('/') or output_folder.endswith('\\')

        if not output_folder:
            output_folder = output_path

        if not output_folder_has_slash_on_end:
            output_folder += '/'

        item_extension = '.{}'.format(input_path.split('.')[-1]).lower()
        key_with_date_created = map_create_date_dict.get(item_extension, None)
        # print('key_with_date_created={}'.format(key_with_date_created))
        if key_with_date_created is None:
            print("Format \"{}\" not supported".format(item_extension))
            return None

        # picture_taken_date = None
        # metadatas = et.get_metadata(input_path)
        # print('metadatas={}'.format(metadatas))
        # sleep(10000)
        # for key in key_with_date_created:
        #     if picture_taken_date is None:
        #         picture_taken_date = metadatas.get(key, None)
        # print(key_with_date_created)
        # print(picture_taken_date)

        from json import JSONDecodeError
        try:
            picture_taken_date = None
            metadatas = et.get_metadata(input_path)
            # print('metadatas={}'.format(metadatas))
            for key in key_with_date_created:
                if picture_taken_date is None:
                    picture_taken_date = metadatas.get(key, None)
            print(key_with_date_created)
            print(picture_taken_date)
        except JSONDecodeError:
            from PIL import Image, ExifTags
            try:
                img = Image.open(input_path)
                # exif_tags = img._getexif()
                exif = {
                    ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in ExifTags.TAGS
                }
                for key in key_with_date_created:
                    if picture_taken_date is None:
                        picture_taken_date = exif.get(key, None)
            except:
                pass

            # print('There was a problem encoding metadata for {}'.format(input_path))
            # print('Final date taken by PIL library: {}'.format(picture_taken_date))
            # print('Available tags form PIL library:')
            # print(exif)
        # except:
        #     picture_taken_date = None
        #     e = sys.exc_info()[0]
        #     print('Error: {}'.format(e))

        if not picture_taken_date or picture_taken_date.isspace():
            print("File \"{}\" has missing date attribute.".format(os.path.abspath(input_path)))
            return None

        date_split = picture_taken_date.split(':')

        if int(date_split[0]) < 2008:  # check if wrong date on camera was set
            return None

        result = output_folder + date_split[0] + '/' + date_split[1] + '/'
        return result


def ensure_folder_exist(path=''):
    if not path:
        return None
    else:
        split_path = path.split('/\\')
        existing_path = split_path[0]
        for folder in split_path:
            if not os.path.isdir(existing_path):
                os.makedirs(existing_path)
                existing_path += '/{}'.format(folder)
            else:
                existing_path += '/{}'.format(folder)


def remove_empty_folders(path_to_cleanup, counter=[0], root=''):
    if not root:
        root = path_to_cleanup
    if os.path.isdir(path_to_cleanup) and not path_to_cleanup.endswith('/'):
        path_to_cleanup += '/'
    input_folder = os.listdir(path_to_cleanup)
    for item_name in input_folder:
        if os.path.isdir(path_to_cleanup + item_name):
            remove_empty_folders(path_to_cleanup + item_name, counter, path_to_cleanup)
    if len(os.listdir(path_to_cleanup)) == 0 and path_to_cleanup != root:
        counter[0] = counter[0] + 1
        os.rmdir(path_to_cleanup)
    return counter


def get_set_of_all_files(folder_path='', result={}, counter=0):
    if os.path.isdir(folder_path) and not folder_path.endswith('/'):
        folder_path = folder_path + '/'

    # result = {()};
    file_absolute_paths = {}
    input_folder = os.listdir(folder_path)
    for entry in input_folder:
        path = folder_path + entry
        if os.path.isfile(path):
            # key_template = namedtuple('name', 'size')
            # key = key_template(os.path.basename(entry), os.stat(path))
            key = (os.path.basename(entry), os.stat(path).st_size)
            # result.add((os.path.basename(entry), os.stat().st_size))
            try:
                abs_path = os.path.abspath(folder_path + entry)
                result[key] = abs_path
            except:
                print('Duplicate hit {}'.format(abs_path))
        elif os.path.isdir(path):
            get_set_of_all_files(folder_path + entry, result)

    return result

def run_as_cli():
    print('''
    =============================================================================
    |  This program organizes pictures based on their exif data.                |
    |  Program moves files from input location to the output location.          |
    |  Inside output location program creates folders structure as follows:     |
    |  Output/Year/Month                                                        |
    |  For example Output/2019/0245                                             |
    |  All pictures which were taken that month will be moved to this location  |
    ============================================================================|
    ''')
    print('''Insert input folder path. Examples:
    D:/Pictures/Input
    ./Input
    ''')
    is_user_input_correct = False
    input_path = input('Input folder path: ')
    input_path = input_path.replace('\\', '/')
    canceled = False
    while not os.path.isdir(input_path) and not canceled:
        print('Folder does not exist')
        input_path = input('Reenter input path or type \"exit\" to terminate: ')
        input_path = input_path.replace('\\', '/')
        if input_path.lower() == 'exit':
            canceled = True

    if not canceled:
        initial_input_path = input_path
        output_path = input('Output folder path: ')
        output_path = output_path.replace('\\', '/')
        while not os.path.isdir(output_path) and not canceled:
            print('Folder does not exist')
            output_path = input('Reenter output path or type \"exit\" to terminate: ')
            output_path = output_path.replace('\\', '/')
            if output_path.lower() == 'exit':
                canceled = True

    if not canceled:
        print('All files new paths:')
        stopwatch_start = time.time()
        with exiftool.ExifTool() as et:
            files_moved = organize_files_in_output_folder(input_path)
            print("Files segregated: {}".format(files_moved))

        file_removed_count = remove_empty_folders(input_path, [0])
        print('{} empty folders in Input folder removed.'.format(file_removed_count))
        print('Operation took {} seconds'.format(time.time() - stopwatch_start))
        input('Press any key to exit')

def get_path_with_slashes(path):
    return path.replace('\\', '/')

def is_directory_path(path):
    return os.path.isdir(path)

def organize_photos(input_path, output_path):
    slash_path = get_path_with_slashes(input_path)
    if not is_directory_path(slash_path):
        print (slash_path + ' is not directory')
        return

    stopwatch_start = time.time()
    with exiftool.ExifTool() as exift:
        global et
        et = exift 
        files_moved = organize_files_in_output_folder(input_path, output_path)
        print("Files segregated: {}".format(files_moved))

    file_removed_count = remove_empty_folders(input_path, [0])
    print('{} empty folders in Input folder removed.'.format(file_removed_count))
    print('Operation took {} seconds'.format(
        time.time() - stopwatch_start))

def organize_registered_folders():
    print('in method organize_registered_folders')
    for key in directories_to_organize:
        print('processing: ' + key)
        input_dir_path = key
        output_dir_path = directories_to_organize[key]
        organize_photos(input_dir_path, output_dir_path)

'''
def log(input):
    log_file_path =  + '/' + LOG_FILE
    with open(log_file_path, 'a') as myfile:
        myfile.write("input")
        '''

if __name__ == "__main__":
   run_as_cli()
