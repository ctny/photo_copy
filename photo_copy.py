# Purpose:  Copy photos from one directory to another, sort into date stamped
#           folders. Typically used to download photos from CF or SD cards to
#           PC. Will write a history file back to the memory card to avoid
#           copying the same files again.
#
# Author:   Clayton Tang, 12/26/2016

import sys
import getopt
import os
import time
import shutil


def usage():
    print('%s -i <input directory to copy from> -o <output directory to copy to>'
          % os.path.basename(sys.argv[0]))
    return


def parse_args():
    my_input_root = ''
    my_output_root = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
    except getopt.GetoptError as err:
        print (err)
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(sys.argv[0], usage)
            sys.exit()
        elif opt == "-i":
            my_input_root = arg
        elif opt == "-o":
            my_output_root = arg

    if my_input_root == '' or my_output_root == '':
        usage()
        sys.exit(2)

    return my_input_root, my_output_root


def read_hist_log(my_hist_log):
    my_hist_files = []

    print('History Log = %s' % my_hist_log)
    if os.path.isfile(my_hist_log):
        print('Log exists')
        with open(my_hist_log) as fo:
            my_hist_files = fo.read().splitlines()
        print("Found %d photos in log" % len(my_hist_files))
    else:
        print("No history log")
    return my_hist_files


def scan_input_root(my_input_root, my_hist_files):
    my_good_files = []
    my_work_files = []
    my_skip_files = []

    # figure out what files to copy
    for root, dirs, files in os.walk(my_input_root):
        for name in files:
            full_path = os.path.join(root, name)
            # print "Found =", root, name, full_path

            if ('.jpg' in name.lower() or
                        '.dng' in name.lower() or  # android raw format
                        '.cr2' in name.lower() or  # canon raw format
                        '.png' in name.lower() or
                        '.arw' in name.lower() or
                        '.mp4' in name.lower() or
                        '.jpeg' in name.lower() or
                        '.avi' in name.lower() or
                        '.mov' in name.lower()):
                my_good_files.append(full_path)
                if full_path not in my_hist_files:
                    my_work_files.append(full_path)
                    # print "Work =", full_path
            else:
                my_skip_files.append(full_path)
                print("SKIP %s" % name)
    print("Skipped %d files, found %d good files, and will copy %d new files"
          % (len(my_skip_files), len(my_good_files), len(my_work_files)))
    return my_good_files, my_work_files


def write_hist_log(my_hist_log, my_good_files):
    with open(my_hist_log, 'w') as fo:
        print('Update log %s' % my_hist_log)
        fo.writelines(["%s\n" % f for f in my_good_files])
    return


def copy_photos(my_output_root, my_work_files):
    i = 0
    for input_file in my_work_files:
        # find file time
        file_time = '0000_00_00'
        if os.lstat(input_file).st_mtime > 0:
            file_time = os.lstat(input_file).st_mtime
            how = 'mtime'
        else:
            file_time = os.lstat(input_file).st_ctime
            how = 'ctime'
        time_str = time.strftime("%Y_%m_%d", time.localtime(file_time))

        # make target dir if needed
        dst_dir = os.path.join(my_output_root, time_str)
        if not os.path.exists(dst_dir):
            print("mkdir %s" % dst_dir)
            os.makedirs(dst_dir)

        # copy file
        i += 1
        print("%d sec, %d of %d = %s -> %s by %s"
              % (int(time.time() - start_time), i,
                 len(my_work_files), input_file, dst_dir, how))
        shutil.copy2(input_file, dst_dir)
    return


start_time = time.time()

if __name__ == '__main__':
    input_root, output_root = parse_args()
    print('Input Dir = %s' % input_root)
    print('Output Dir = %s' % output_root)

    if os.path.exists(input_root):
        hist_log = os.path.join(input_root, 'python_download.log')
        hist_files = read_hist_log(hist_log)

        good_files, work_files = scan_input_root(input_root, hist_files)

        copy_photos(output_root, work_files)

        write_hist_log(hist_log, good_files)
    else:
        print("Cannot access %s" % input_root)

    # don't let dos window auto close by asking for a key press
    #print "Press <Enter> to exit"
    #raw_input()
    print("Done")
