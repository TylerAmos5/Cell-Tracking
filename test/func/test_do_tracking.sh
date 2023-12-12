test -e ssshtest || wget -q https://raw.githubusercontent.com/ryanlayer/ssshtest/master/ssshtest
. ssshtest

run test_do_tracking python src/do_tracking.py --file_path "doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2"
assert_equal $"WellD01_ChannelmIFP,mCherry,YFP_Seq0000_tracks.csv" $( ls $"WellD01_ChannelmIFP,mCherry,YFP_Seq0000_tracks.csv")
assert_exit_code 0