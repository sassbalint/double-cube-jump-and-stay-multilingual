# Language independency of the “jump and stay” method

## What is this all about?

We take the [“jump and stay” method](https://github.com/sassbalint/double-cube-jump-and-stay) and show that this method is language independent
by running it for some UD corpora in the following languages:
Czech, Dutch, English, Finnish, German, Hungarian,
Norwegian, Turkish and Wolof.

[Paper](...).

## Usage

Please type:

`make`

Doing this,
final output is created in `result` directory using corpora from `input`.

The newly created output can be compared to
the original saved version:
`make result_pVCC_diff`

Tested on Debian Linux. (May work on other operation systems...)

Requirements:
python 3
make

## How does it work?

`process_conll.py` processes the UD corpora to run the
“jump and stay” implementation `impl.py` on them.

`impl.py` and `Makefile.jands` are taken from the
“jump and stay” method repo (commit f3ca1ec):
https://github.com/sassbalint/double-cube-jump-and-stay/commit/f3ca1ec

## License

If you want to use this, please cite the above paper and contact me. :)
No warranty, sorry.

