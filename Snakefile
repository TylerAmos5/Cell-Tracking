
rule all:
    input:
        'output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2_tracks.csv'

rule download_test_file:
    output:
        'doc/test.nd2'
    shell:
        'wget -O {output} "https://drive.google.com/file/d/1S9cvdLpFNgGg9cJg9Rt2NduSpoacPYSZ/view?usp=drive_link"'


rule do_tracking:
    input:
        'doc/test.nd2'
    output:
        'output/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2_tracks.csv'
    shell:
        'python src/do_tracking.py --file_path="doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2" --output_path="output"'