import time
import subprocess
import os
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    import sys
    subprocess.check_call([sys.executable,"-m","pip","install","watchdog"])


class Handler(FileSystemEventHandler):
    def __init__(self,observer):
        try:
            self.process=subprocess.Popen(['python','TRDC meal.py'])
            self.observer=observer
        except:
            self.process=None
    
    def run_new(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process=subprocess.Popen(['python','TRDC meal.py'])
    
    def on_modified(self,event): ##當指定監控資料夾有更改,就觸發
        if not event.is_directory:
            mfile=event.src_path
            if 'TRDC meal.py' in mfile or 'login.json' in mfile:
                self.run_new()
            elif 'modified watchdog.py' in mfile:
                try:
                    self.destroy()
                    subprocess.Popen(['python','modified watchdog.py'])#
                    raise KeyboardInterrupt
                except KeyboardInterrupt:
                    self.observer.stop()
    def destroy(self): ##看門狗結束前會把監控程式也關閉
        self.process.terminate()
         
if __name__=='__main__':
    path=os.path.dirname(os.path.abspath(__file__)) 
    observer=Observer() ##監控
    event_handler=Handler(observer) 
    observer.schedule(event_handler,path=path,recursive=True)#
    observer.start() 
    try:
        while(True):
            time.sleep(1)
    except KeyboardInterrupt:
        event_handler.destroy()
        observer.stop()
    observer.join()
