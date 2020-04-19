import getopt

""" Class to store settings configuration """
class Settings():
    def __init__(self):
        self.input_source ="";
        self.output_name ="cam"
        self.record_video = True # Added from original script
        self.cam_name =""
        self.show_input = False
        self.seconds_after = 5
        self.counter_start = 0
        self.debug = 0
        self.area = 600
        self.noise = 21
        self.fps = 5
        self.frames_trigger = 2
        self.timestamp = False
        self.mask_template = False
        self.mask_file = ""
        self.command = ""
        self.draw_contours = False
        self.max_width = 640
        self.backend = 0 # Added from original script
    
    def load_from_args(self, argv):
        optlist, args = getopt.getopt(argv, "i:o:sa:b:c:d:ht:n:l:Dgm:f:k:x:CM:r")

        # Do not print help if it's not requested
        print_usage = False
                
        for o, arg in optlist:
            if o in "-i":
                self.input_source = arg
            elif o in "-o":
                self.output_name = arg
            elif o in "-s":
                self.show_input = True              
            elif o in "-a":
                self.seconds_after = int(arg)
            elif o in "-b":
                self.backend = int(arg)
            elif o in "-c":
                self.counter_start = int(arg)
            elif o in "-d":
                self.debug = int(arg)
            elif o in "-h":
                print_usage = True
            elif o in "-t":
                self.area = int(arg)
            elif o in "-n":
                self.noise = int(arg)
            elif o in "-l":
                self.cam_name = arg
            elif o in "-D":
                self.timestamp = True
            elif o in "-g":
                self.mask_template = True
            elif o in "-m":
                self.mask_file = arg
            elif o in "-f":
                self.fps = int(arg)
            elif o in "-k":
                self.frames_trigger = int(arg)
            elif o in "-x":
                self.command = arg
            elif o in "-C":
                self.draw_contours = True
            elif o in "-M":
                self.max_width = int(arg)
            elif o in "-r":
                self.record_video = False
            else:
                print_usage = True

        # Frame display
        if(self.debug > 4):
            print("Error: debug step doesn't correspond to a valid number.")
            print_usage = True

        # Backend selection
        if(self.backend > 2):
            print("Error: not valid backend number")
            print_usage = True

        # Odd Gaussian matrix size
        if((self.noise % 2) == 0):
            self.noise = self.noise + 1

        # If print_usage return error code
        if(print_usage):
            self.print_usage()
            return 1

        # Exit OK
        return 0
        
    
    def print_usage(self):
        print("Usage: python -m camodet [options]")
        print("Options: ")
        print("    -h              Print this help message.")
        print("    -i input_video: The source for motion detection.")
        print("    -o output_name: The name for the output recordings.")
        print("                    A number and extension will be automatically added after it:")
        print("                      e.g. output_name23.avi")
        print("    -b number:      Selects backend of OpenCv VideoCaptureAPI")
        print("                    0 Auto | 1 FFMPEG | 2 DirectShow (videoInput)")
        print("    -s:             Open window showing the input video.")
        print("    -D:             Date and time labelled to video.")
        print("    -a seconds:     Seconds to record after the motion has stopped.")
        print("    -c number:      Counter number to skip using in the output name (Default 0).")
        print("    -g              Interactive ROI mask generation (saved as roi_mask.png)")
        print("    -l cam_name:    Label camera name on video.")
        print("    -m mask_image:  Mask image to use for ROI motion detection. Black areas are ignored, White areas checked.")
        print("    -t number:      Threshold area (sqare pixels) to trigger detection.") 
        print("                    Movements below this area are ignored (Default 600).")
        print("    -n number:      Noise reduction level (Default 21).")
        print("    -f number:      FPS to process from input source (Default 5).")
        print("    -k number:      Number of consecutive frames with motion to trigger motion event (Default 2).")
        print("    -x command:     Command to be executed when motion is detected.")
        print("    -M number:      Max width of frame to be processed for motion detection, if input is larger it will be downsized to this value. (Default 640).")
        print("    -d number:      Show intermediate images in a debug window. Number can be:")
        print("                    0: None | 1: noise reduction | 2: frames difference | 3: threshold | 4:dilated(final).")
        print("    -r              Skip Record into a file to avoid loading HDD during debug.")
