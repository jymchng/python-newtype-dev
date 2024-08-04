python -m setup clean && rm -f newtypemethod.cpython-310-x86_64-linux-gnu.so && rm -f newtypeinit.cpython-310-x86_64-linux-gnu.so && python -m setup build_ext --inplace && python -m pytest . -s -vv

python -m setup clean && rm -f newtypemethod.cpython-310-x86_64-linux-gnu.so && rm -f newtypeinit.cpython-310-x86_64-linux-gnu.so && python -m setup build_ext --inplace && python -m pytest test_nric.py -s -vv

python -m setup clean && rm -f newtypemethod.cpython-310-x86_64-linux-gnu.so && rm -f newtypeinit.cpython-310-x86_64-linux-gnu.so && python -m setup build_ext --inplace && python -m pytest test_custom_type.py -s -vv

python -m setup clean && rm -f newtypemethod.cpython-310-x86_64-linux-gnu.so && rm -f newtypeinit.cpython-310-x86_64-linux-gnu.so && python -m setup build_ext --inplace && python -m pytest test_free_standing.py -s -vv

python -m setup clean && rm -f newtypemethod.cpython-310-x86_64-linux-gnu.so && rm -f newtypeinit.cpython-310-x86_64-linux-gnu.so && python -m setup build_ext --inplace && python -m pytest test_slots.py -s -vv