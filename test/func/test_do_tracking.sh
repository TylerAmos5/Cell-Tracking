test -e ssshtest || wget -q https://raw.githubusercontent.com/ryanlayer/ssshtest/master/ssshtest
. ssshtest

wget -O 'test.nd2' "https://drive.google.com/file/d/1S9cvdLpFNgGg9cJg9Rt2NduSpoacPYSZ/view?usp=sharing" # add google drive link here
run test_do_tracking python src/do_tracking.py --file_path "test.nd2"
assert_equal $"tracks.csv" $( ls $"tracks.csv")
assert_exit_code 0