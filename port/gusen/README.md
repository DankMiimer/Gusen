# Gusen

A top-down adventure in the style of a GBA game, made with LÖVE 11.5.
Built for and tested on the Anbernic RG34XXSP (720×480, exactly 3× the
game's 240×160 screen).

## Controls

| Button | Action |
|---|---|
| D-pad / left stick | Move |
| A | Talk / read / (sword, coming in M1) |
| B | Item (coming later) |
| Start | Pause menu (language, A/B setup, quit) |
| Select + Start | Force quit (gptokeyb hotkey) |

The first time you start the game it asks you to **press A**. Whatever button
you press becomes A (and its neighbour becomes B), so the layout is right
whichever way your firmware maps the buttons. Change it later in the pause
menu under *Set up A/B*.

## Files

* `gamedata/`: the LÖVE game
* `saves/`: settings and saves (keep this folder when updating)
* `log.txt`: output from the last run

## Thanks

Pixel art by DankMiimer. Built on LÖVE (zlib licence) and PortMaster.
