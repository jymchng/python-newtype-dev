

test-all:
	python -m setup clean && rm -f newtypemethod.cpython-310-x86_64-linux-gnu.so && rm -f newtypeinit.cpython-310-x86_64-linux-gnu.so && python -m setup build_ext --inplace && python -m pytest . -s -vv