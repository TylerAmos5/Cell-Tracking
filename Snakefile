
rule all:
    input:
        'output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2_tracks.csv'

rule do_tracking:
    input:
        'doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2'
    output:
        'output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2_tracks.csv'
    shell:
        'python src/do_tracking.py --file_path="{input}" --output_path="{output}"'