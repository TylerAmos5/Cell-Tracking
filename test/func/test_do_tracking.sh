test -e ssshtest || wget -q https://raw.githubusercontent.com/ryanlayer/ssshtest/master/ssshtest
. ssshtest

wget -O 'test.nd2' "https://docs.google.com/......." # add google drive link here
run test_do_tracking python src/do_tracking.py --fire_file_name "test.nd2."
assert_equal $"tracks.csv" $( ls $"tracks.csv")
assert_exit_code 0