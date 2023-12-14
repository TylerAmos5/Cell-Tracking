test -e ssshtest || wget -q https://raw.githubusercontent.com/ryanlayer/ssshtest/master/ssshtest
. ssshtest

run test_do_tracking python src/do_tracking.py --file_path "doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2" --output_path="output"
assert_equal $"output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000_tracks.csv" $( ls $"output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000_tracks.csv")
assert_equal $"channel2_plots" $( ls $"output" | grep "channel2")
assert_equal $"Cell_0.png" $( ls $"output/channel2_plots")
assert_exit_code 0