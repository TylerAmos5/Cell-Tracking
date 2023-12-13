rule all:
    input:
        'output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000_tracks.csv'

rule do_tracking:
    input:
        'doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2'
    output:
        'output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000_tracks.csv'
    shell:
        'python src/do_tracking.py --file_path=doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2 --output_path=output'