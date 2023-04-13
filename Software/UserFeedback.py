from Data import Timestamp, Run
import datetime
import time

class MyClass:
    def __init__(self):
        self.timestamps_list = []
       



      

    def User_Alerts(self, timestamps_list : list, target_temp : float):
         self.timestamps_list = timestamps_list
         print(self.timestamps_list)
         for x in self.timestamps_list:
            print(x.unix_time,x.louverPos,x.temperature,x.motion)

         self.initial_value = self.timestamps_list[-1].temperature
         self.latest_value = self.timestamps_list[0].temperature
         print("Initial value is ", self.initial_value, "and the latest value is ", self.latest_value)
        
         self.target_temp = target_temp
         print("target temperature is ",self.target_temp)
         

        

                  
        
            
         





if __name__ == "__main__":
    my_timestamp_000 = Timestamp(100, 72.1, True)
    time.sleep(2)
    my_timestamp_00 = Timestamp(110, 73, True)
    time.sleep(2)
    my_timestamp_01 = Timestamp(115, 73.8, False)
    time.sleep(2)
    my_timestamp_0 = Timestamp(120, 75, True)

    my_run = Run(75)
   

    my_run.createTimestamp(my_timestamp_000)
    my_run.createTimestamp(my_timestamp_00)
    my_run.createTimestamp(my_timestamp_01)
    my_run.createTimestamp(my_timestamp_0)
    my_class = MyClass()

    my_class.User_Alerts(my_run.timestamps, my_run.target)


