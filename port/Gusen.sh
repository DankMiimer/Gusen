#!/bin/bash
# Gusen - PortMaster launcher.
# Target device: Anbernic RG34XXSP (720x480 = exactly 3x the game's 240x160).

XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

source $controlfolder/control.txt
[ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"
get_controls

GAMEDIR="/$directory/ports/gusen"
cd "$GAMEDIR"

# Log everything to gusen/log.txt (send this file along if something goes wrong)
> "$GAMEDIR/log.txt" && exec > >(tee "$GAMEDIR/log.txt") 2>&1

# Settings and saves live next to the game: gusen/saves/love/gusen/
export XDG_DATA_HOME="$GAMEDIR/saves"
mkdir -p "$XDG_DATA_HOME"
export SDL_GAMECONTROLLERCONFIG="$sdl_controllerconfig"
export GUSEN_DEVICE=1

LOVE_TXT="$controlfolder/runtimes/love_11.5/love.txt"
if [ ! -f "$LOVE_TXT" ]; then
  echo "Gusen needs the LOVE 11.5 runtime that ships with PortMaster: update PortMaster and try again."
  type pm_message >/dev/null 2>&1 && pm_message "Gusen needs LOVE 11.5: please update PortMaster."
  sleep 5
  exit 1
fi
source "$LOVE_TXT"

$GPTOKEYB "$LOVE_GPTK" &
pm_platform_helper "$LOVE_BINARY"
$LOVE_RUN "$GAMEDIR/gamedata"

pm_finish
