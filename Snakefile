
rule all:
    input:
        "tracks.csv"

rule download_test_file:
    output:
        "test.nd2"
    shell:
        wget -O {output} "https://drive.google.com/file/d/1S9cvdLpFNgGg9cJg9Rt2NduSpoacPYSZ/view?usp=sharing"


rule do_tracking:
    input:
        "test.nd2"
    output:
        "tracks.csv"  # Output file
    shell:
        "python src/do_tracking.py --file_path='test.nd2'"