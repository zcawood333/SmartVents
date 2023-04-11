from Data import Timestamp, Run
import datetime
import time

class MyClass:
    def __init__(self):
        self.timestamps_list = []
        self.start_index = 0
        self.target_index = -1

      

    def User_Alerts(self, timestamps_list : list):
         self.timestamps_list = timestamps_list
         print(self.timestamps_list)

                  
         for x in self.timestamps_list:
             print(x.unix_time,x.louverPos,x.temperature,x.motion)
            
         





if __name__ == "__main__":
    my_timestamp_000 = Timestamp(100, 72.1, True)
    time.sleep(2)
    my_timestamp_00 = Timestamp(110, 73, True)
    time.sleep(2)
    my_timestamp_01 = Timestamp(115, 73.8, False)
    time.sleep(2)
    my_timestamp_0 = Timestamp(120, 75, True)

    my_run = Run(75)
    my_class = MyClass()

    my_run.createTimestamp(my_timestamp_000)
    my_run.createTimestamp(my_timestamp_00)
    my_run.createTimestamp(my_timestamp_01)
    my_run.createTimestamp(my_timestamp_0)

    my_class.User_Alerts(my_run.timestamps)


