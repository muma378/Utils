import log
class filter_audio(object):
    
    def __init__(self):
        self.log = log.my_log.instance()

    def filter_by_time(self,audio_path,time_len):
        if float(time_len) >= 1.0 and float(time_len) <= 20.0:
            return True
        else:
            self.log.set_warning_log('Time Unqualified:'+audio_path)
            return False

if __name__ == "__main__":
    filter_audio_wav = fileter_audio()
    
