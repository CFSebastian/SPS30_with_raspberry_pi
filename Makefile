# See user_config.inc for build customizations
-include user_config.inc
include default_config.inc

.PHONY: all clean

all: sps30_example_usage connect_python_sps

sps30_example_usage: clean_sps30
	$(CC) $(CFLAGS) -o $@ ${sps30_uart_sources} ${uart_sources} ${sps30_uart_dir}/sps30_example_usage.c

connect_python_sps: clean_connect
	$(CC) $(CFLAGS) -o $@ ${sps30_uart_sources} ${uart_sources} ${sps30_uart_dir}/connect_python_sps.c

clean: clean_sps30 clean_connect

clean_sps30:
	$(RM) sps30_example_usage

clean_connect:
	$(RM) connect_python_sps
