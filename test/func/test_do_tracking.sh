test -e ssshtest || wget -q https://raw.githubusercontent.com/ryanlayer/ssshtest/master/ssshtest
. ssshtest

run test_do_tracking python src/do_tracking.py --file_path "doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2" --output_path="output"
assert_equal $"output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000_tracks.csv" $( ls $"output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000_tracks.csv")
assert_equal $"output/channel2_plots/Cell_*.png" $( ls $"output/channel2_plots/Cell_*.png")
assert_equal $"output/channel3_plots/Cell_*.png" $( ls $"output/channel3_plots/Cell_*.png")
assert_exit_code 0