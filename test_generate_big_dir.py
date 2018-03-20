import os


if __name__ == "__main__":

    if not os.path.isdir("big_dir"):
        os.mkdir("big_dir")

    for i in range(100):

        if not os.path.isdir("big_dir/" + str(i)):
            os.mkdir("big_dir/" + str(i))

        for j in range(10000):
            open("big_dir/" + str(i) + "/file-" + str(j), 'a').close()
