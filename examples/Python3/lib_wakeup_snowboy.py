import sys
from . import snowboydecoder
import signal

class HotwordDetector:
    def __init__(self, model_path, sensitivity=0.5, detected_callback=None):
        self.model_path = model_path
        self.sensitivity = sensitivity
        self.detected_callback = detected_callback or snowboydecoder.play_audio_file
        self.detector = snowboydecoder.HotwordDetector(
            self.model_path, 
            sensitivity=self.sensitivity
        )
        self.interrupted = False
        self.original_signal_handler = None

    def _signal_handler(self, signal, frame):
        self.interrupted = True

    def _interrupt_check(self):
        return self.interrupted

    def start(self):
        # 保存原始信号处理器以便恢复
        self.original_signal_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        print('Listening... Press Ctrl+C to exit')
        try:
            self.detector.start(
                detected_callback=self.detected_callback,
                interrupt_check=self._interrupt_check,
                sleep_time=0.03
            )
        finally:
            # 恢复原始信号处理器
            signal.signal(signal.SIGINT, self.original_signal_handler)
            self.cleanup()

    def stop(self):
        self.interrupted = True

    def cleanup(self):
        self.detector.terminate()

# 使用示例
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python script.py model.path")
        sys.exit(1)

    def custom_callback():
        print("Hotword detected!")
        # 在这里添加自定义处理逻辑

    detector = HotwordDetector(
        model_path=sys.argv[1],
        detected_callback=custom_callback
    )
    
    try:
        detector.start()
    except KeyboardInterrupt:
        detector.stop()
    finally:
        detector.cleanup()
