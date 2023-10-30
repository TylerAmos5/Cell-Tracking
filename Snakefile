
rule all:
    input:
        "tracks.csv"

rule do_tracking:
    output:
        "tracks.csv"  # Output file
    shell:
        "python src/do_tracking.py --file_path='/Users/tyleramos/Cell-Tracking/doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2'"
