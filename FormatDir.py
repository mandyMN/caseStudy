from os import makedirs
from os.path import join


class FormatDirectoryHierarchy(object):
    '''
        class creating the folder hierarchy given the number of the questions
    '''
    def create_directory(self, main_dir, questions):
        for i in range(1, questions+1):
            directory = join(main_dir, 'Q' + str(i))
            makedirs(directory, exist_ok=True)
        return