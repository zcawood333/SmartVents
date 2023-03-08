OBJS = main.o Vent.o
CC = g++
INCLUDES = Vent.h Data.h
LIBS = Data.h
CFLAGS = -Wall -g
EXECUTABLE = main
COMMANDLINE =

.DEFAULT_GOAL := run

.PHONY : run
run : $(EXECUTABLE)
	./$(EXECUTABLE) $(COMMANDLINE)

cleanmake : clean $(EXECUTABLE)

.PHONY : $(EXECUTABLE)
$(EXECUTABLE) : $(OBJS)
	$(CC) $(CFLAGS) -o $(EXECUTABLE) $(OBJS) $(INCLUDE) $(LIBS) 

%.o : %.c  %.h
	$(CC) $(CFLAGS) -c $@ $(HEADDERS) $(INCLUDE) $(LIBS)

clean :
	rm $(EXECUTABLE) ${OBJS} 