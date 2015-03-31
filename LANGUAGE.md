###Dowload###

You can download `Language Pack File` from https://lp.getpebble.com/v1/languages

>Now there are files for `German`, `Spanish`, `French`, `English` and `Chinese`.

There are different files for specific hardware, but I found they seem identical although their filenames are different.
  
###Unpack###

`Language Pack File` has extension `.pbl` for filename, and it is just a special `Pebble Resource File`

You can `unpack` it by `pbpack` tool in `Pebble SDK`.

>This script may help you: https://github.com/xndcn/pebble-firmware-utils/blob/for-language-pack/pbpack_tool.py

There will be `19` raw files unpacked from `Language Pack File`, named from `000`, `001`, to `018`
  
###Localization###

The first file `000`, is a `GNU message catalog` file, which should has an extension `.mo` usually

This file can be transformed to `.po` file by `msgunfmt 000 -o 000.po`

`000.po` will be a `GNU gettext message` file which contains original strings and localized translation.

You can change it and transform back by `msgfmt 000.po -o 000`

###Fonts###

The other files, `001` to `018`, are either `Pebble Font File` or just empty file

>You can extract codepoints from the font file by using https://github.com/xndcn/pebble-firmware-utils/blob/for-language-pack/extract_codepoints.py
  
And then you can replace the font file by `fontgen.py` in Pebble SDK with your favorite font.

However, I didn't find any font file from `Language Pack File` except `Chinese`

In Chinese pbl, there are `4` types font file. 
  
  >`001` and `002` are identical, which contains only `217` characters and their maximum height is 14.
  
  >`003` and `004` are identical, which contains `9056` characters and their maximum height is 18.
  
  >`005`, `006`, `007`, `008` are identical, which also contains `9056` characters and their maximum height is 24.
  
  >`016` contains only `12` characters for `month` names and its height is 21.
  
  >Other files are empty.

---

  I think the order of font file is corresponding to its resource id:
  
  File |  Font
-------|---------
  001  |  GOTHIC_14
  002  |  GOTHIC_14_BOLD
  003  |  GOTHIC_18
  004  |  GOTHIC_18_BOLD
  005  |  GOTHIC_24
  006  |  GOTHIC_24_BOLD
  007  |  GOTHIC_28
  008  |  GOTHIC_28_BOLD
  009  |  BITHAM_30_BLACK
  010  |  BITHAM_42_BOLD
  011  |  BITHAM_42_LIGHT
  012  |  BITHAM_42_MEDIUM_NUMBERS
  013  |  BITHAM_34_MEDIUM_NUMBERS
  014  |  BITHAM_34_LIGHT_SUBSET
  015  |  BITHAM_18_LIGHT_SUBSET
  016  |  ROBOTO_CONDENSED_21
  017  |  ROBOTO_BOLD_SUBSET_49
  018  |  DROID_SERIF_28_BOLD

###Conclusion###
What can we do by modifying `Language Pack File`?

1. You can do localization or custom system strings as you like.
  
2. You can replace the system font with `your favorite font`.

---

At last, after changing those resources, you can repack to a new.pbl and put it inside your mobile phone, then you can open it by `Pebble App` to install.
