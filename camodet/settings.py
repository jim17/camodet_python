""" Class to store settings configuration """
class Settings():
    def __init__(self):
        self.input_source ="";
        self.output_name ="cam"
        self.record_video = False # Added from original script
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
        self.draw_contours = True
        self.max_width = 640
    
    def load_from_args(self, argc=0, *argv):
        pass
    
    def print_usage(self):
        print("Usage: python -m camodet [options]")
        print("Options: ")
        print("    -h              Print this help message.")
        print("    -i input_video: The source for motion detection.")
        print("    -o output_name: The name for the output recordings.")
        print("                    A number and extension will be automatically added after it:")
        print("                      e.g. output_name23.avi")
        print("    -s:             Open window showing the input video.")
        print("    -D:             Date and time labelled to video.")
        print("    -a seconds:     Seconds to record after the motion has stopped.")
        print("    -c number:      Counter number to skip using in the output name (Default 0).")
        print("    -g              Generate template image for ROI mask.")
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
        print("                    1: noise reduction | 2: frames difference | 3: threshold | 4:dilated(final).")