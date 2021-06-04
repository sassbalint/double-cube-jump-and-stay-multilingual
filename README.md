# “Jump and stay” method for dependency annotated corpora

## What is this all about?

We use the [“jump and stay” method](https://github.com/sassbalint/double-cube-jump-and-stay) for
extracting proper verb centered constructions (pVCCs):
(1) from UD corpora in different languages
(Czech, Dutch, English, Finnish, German, Hungarian,
Norwegian, Turkish and Wolof)
showing the language independency of the method;
(2) from Hungarian corpora of different genres
dependency-annotated by the
[e-magyar](https://github.com/nytud/emtsv) system
showing that the pVCCs obtained 
appropriately represent the topic of the corpus.

## Usage

Type:

`make INPUT=<inputfile>`

where `<inputfile>` is the name of the input file
placed in the `input` directory.

The output files named `<inputfile>_<verb>.test.out3.pVCC`
are created in the `result` directory.

The newly created output can be compared to
the original saved version:
`make result_pVCC_diff`

Tested on Debian Linux. (May work on other operation systems...)\
Requirements:
`python3` and
`make`

### Usage for UD corpora

`make INPUT=??`

as UD corpora filenames contain two letters.

### Usage for e-magyar corpora

`make INPUT=????`

as e-magyar corpora filenames contain four letters.

### Usage for your own Hungarian text

1. dependency-analyse the text with e-magyar
using `tok,morph,pos,conv-morph,dep,conll` modules,
(see [e-magyar](https://github.com/nytud/emtsv) for details);
2. put the analysed file (e.g. `mycorpus`) into the `input` dir;
3. run `make INPUT=mycorpus`

## How does it work?

`process_conll.py` preprocesses the UD/e-magyar corpora
in order to be able to run the
“jump and stay” implementation `impl.py` on them.

`impl.py` and `Makefile.jands` are taken from the
“jump and stay” method repo (commit `f3ca1ec`):
https://github.com/sassbalint/double-cube-jump-and-stay/commit/f3ca1ec

## License

If you want to use this, please cite the paper below and contact me. :)
No warranty, sorry.

## Citation

If you use this, please cite one of the following papers:

[Sass Bálint. A duplakocka modell és az igei szerkezeteket kinyerő "ugrik és marad" módszer nyelvfüggetlensége, valamint néhány megjegyzés az UD annotáció univerzalitásáról. In: MSZNY 2020, 399-407.](http://real.mtak.hu/114060/1/dc_langindep.pdf)

[Sass Bálint. The "Jump and Stay" Method to Discover Proper Verb Centered Constructions in Corpus Lattices. In : RANLP 2019, 1076-1084.](http://www.nytud.hu/oszt/korpusz/resources/sb_jump_and_stay.pdf)

