CC = g++
CFLAGS = -Wall -c -g -std=c++11
LDFLAGS = 
TARGET = smart_truncate

$(TARGET): main.o audio.o
	$(CC) main.o audio.o -o $(TARGET) $(LDFLAGS)

main.o: main.cpp audio.h
	$(CC) $(CFLAGS) main.cpp

audio.o: audio.cpp common.h audio.h
	$(CC) $(CFLAGS) audio.cpp


clean:
	rm -f *.o *.c~ *.h~ *.log $(TARGET)

