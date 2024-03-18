import os


class FileHandler:
    @staticmethod
    def open_file_with_default_program(file_path):
        """Opens a file using its default program on Windows."""
        try:
            os.startfile(file_path)
            return file_path + " opened successfully"
        except OSError as e:
            return f"Error opening file: {e}"

    @staticmethod
    def get_files_in_directory(directory_path):
        """Returns a dictionary containing lists of files and directories in the given directory."""
        content = {'files': [], 'dirs': []}
        try:
            for item in os.listdir(directory_path):
                full_path = os.path.join(directory_path, item)
                if os.path.isfile(full_path):
                    content['files'].append(full_path)
                elif os.path.isdir(full_path):
                    content['dirs'].append(full_path)
        except OSError as e:
            print(f"Error accessing directory: {e}")
        return content
