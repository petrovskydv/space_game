def get_frame(filename):
    with open(filename, "r") as my_file:
        return my_file.read()