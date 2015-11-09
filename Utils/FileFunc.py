import os, errno
import glob
import json


class FileFunc:
    @staticmethod
    def read_file_into_list(filename):
        with open(filename, 'r') as f:
            data = [line.strip() for line in f]
        return data

    @staticmethod
    def write_list_into_file_append(filename, list):
        with open(filename, 'a') as f:
            for s in list:
                f.write(s + '\n')

    @staticmethod
    def write_list_into_file(filename, list):
        with open(filename, 'w') as f:
            for s in list:
                f.write(s + '\n')

    @staticmethod
    def write_dict_to_file(filename, dict):
        with open(filename, 'w') as f:
            f.write(repr(dict))

    @staticmethod
    def write_json_to_file(filename, dict):
        with open(filename, 'w') as outfile:
            json.dump(dict, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    @staticmethod
    def clear_folder(foldername):
        files = glob.glob(foldername)
        for f in files:
            if f is foldername:
                continue
            try:
                os.remove(f)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    print(e.args[1])
                    raise
