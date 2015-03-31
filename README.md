#Pebble Firmware Utils#
[Pebble Language Pack File Analyse](../for-language-pack/LANGUAGE.md)

Some tools used for Pebble firmware, now include:

##pbpack_tool.py##
unpack: `pbpack_tool.py unpack foo.pbl [output_dir]`

pack: `pbpack_tool.py pack fool.pbl [some raw files to pack]`

It will unpack or pack language file.

`MUST set sdk path environment variable firstly`

##extract_codepoints.py##
Usage: `extract_codepoints.py fontfile > codepoints.json`

It will extract codepoints from pebble font file, and you can use it to re-generate font file by `fontgen.py` in Pebble SDK.

`python $PEBBLE_SDK_PATH/Pebble/common/tools/font/fontgen.py pfo --list codepoints.json --extended HEIGHT OTF_OR_TTF_FONT FONT_FILE`
