.PHONY: run show cat

PROLOG=swipl
TARGET=../kkm/driver/fa01

show: run cat

cat:
	@echo '------ commands.py ----'
	@cat $(TARGET)/commands.py
	@echo '------ api.py ---------'
	@cat $(TARGET)/api.py


run: protogen.pl
	$(PROLOG) -g run protogen.pl
