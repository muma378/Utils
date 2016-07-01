CC = g++
CFLAGS = -Wall -c -g -std=c++11
LDFLAGS = 
TARGET = smart_truncate

$(TARGET): main.o audio.o common.o exceptions.o
	$(CC) main.o common.o audio.o exceptions.o -o $(TARGET) $(LDFLAGS)

main.o: main.cpp audio.h exceptions.h
	$(CC) $(CFLAGS) main.cpp

exceptions.o: exceptions.cpp exceptions.h
	$(CC) $(CFLAGS) exceptions.cpp

audio.o: audio.cpp common.h audio.h exceptions.h
	$(CC) $(CFLAGS) audio.cpp

common.o: common.cpp common.h
	$(CC) $(CFLAGS) common.cpp	


clean:
	rm -f *.o *.c~ *.h~ *.log $(TARGET)


GTEST_DIR = 
CPPFLAGS += 