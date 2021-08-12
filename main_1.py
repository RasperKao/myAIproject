from p import _main_
from glob import glob

h5_files = glob(r"C:\Users\Casper\Desktop\yolov3\keras-yolo3-master\weights\*")
print(h5_files)

# b = _main_(r"C:\Users\Casper\Desktop\yolov3\config.json",
#            r"C:\Users\Casper\Desktop\yolov3\keras-yolo3-master\weights\food.h5",
#            r"C:\Users\Casper\Desktop\yolov3\pic\re43.jpg")

for h5_file in h5_files:
    b = _main_(r"C:\Users\Casper\Desktop\yolov3\config.json",
           h5_file,
           r"C:\Users\Casper\Desktop\yolov3\pic\re64.jpg")
    print(b)

# dirs = glob.glob(r"C:\Users\NTUT219\Desktop\data\valid_image_folder\*")
# print(dir)
#
# j = r"C:\Users\NTUT219\Desktop\data\config.json"
# dic = {}
# for dir in dirs:
#     path = dir.split("\\")[-1]
#     dic[f"{path}"] = _main_(j, dir)
#     print(_main_(j, dir))
# print(dic)
