CC = g++
CFLAGS = -Wall -c -g -std=c++11
LDFLAGS = 
TARGET = smart_truncate

$(TARGET): main.o audio.o common.o
	$(CC) main.o common.o audio.o -o $(TARGET) $(LDFLAGS)

main.o: main.cpp audio.h exceptions.h
	$(CC) $(CFLAGS) main.cpp

audio.o: audio.cpp common.h audio.h exceptions.h
	$(CC) $(CFLAGS) audio.cpp

common.o: common.cpp common.h
	$(CC) $(CFLAGS) common.cpp	


clean:
	rm -f *.o *.c~ *.h~ *.log $(TARGET)

