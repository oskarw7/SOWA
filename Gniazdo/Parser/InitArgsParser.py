import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-d", "--ext_detection" , help="use this flag to use external detection", action="store_true")
arg_parser.add_argument("-mm", "--ext_middle_module", help="use external middle_module connected with serial port /dev/tty*")
arg_parser.add_argument("-cc", "--console_control", help="use stdin as input for camera movement", action="store_true")
arg_parser.add_argument("-v", "--visualize", help="start streaming visualization", action="store_true")
arg_parser.add_argument("-ar", "--auto_reset", help="automatically reset the camera orientation to the drone", action="store_true")




