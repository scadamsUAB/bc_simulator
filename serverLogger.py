import io
import datetime
class serverLogger:
    def __init__(self,filename,overwrite=True):
        self.__filename=filename
        if(overwrite):
            self.initialize()
    
    def initialize(self):
        myfile=open(self.__filename,"w")
        myfile.write(str(datetime.datetime.utcnow())+"--- STARTING NEW LOG \n")
        myfile.close()
    
    def appendLog(self,message):
        myfile=open(self.__filename,"a")
        myfile.write(str(datetime.datetime.utcnow())+"--- "+str(message)+"\n" )
        myfile.close()


if __name__=="__main__":
    mylogger=serverLogger("TESTLOG.txt")
    mylogger.appendLog("TEST MESSAGE")
