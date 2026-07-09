CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -g -O0

SRC = server.c
OUT = matomomorun

$(OUT): $(SRC)
	$(CC) $(CFLAGS) -o $(OUT) $(SRC)
clean:
	rm -f $(OUT)
