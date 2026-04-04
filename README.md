# Confidant Ability Randomizer

Randomizes which rank of which Confidant gives which abilities in Persona 5 Royal. Intended for use on PC with Reloaded-II.

## To Use

This mod requires Python to use https://www.python.org/downloads/

Install the `p5rpc.confidantabilityrandomizer` mod to Reloaded-II. In your mod list, right click "Open Folder" and navigate to the `FEmulator/PAK/INIT/CMM.BIN` folder. Inside will be the files `cmmFunctionTable.ctd` and `randomize.py`; I recommend making a copy of `cmmFunctionTable.ctd` and renaming it or placing it elsewhere if you ever want to re-randomize. Run `randomize.py` to modify `cmmFunctionTable.ctd`, then enable Confidant Ability Randomizer in Reloaded. You can optionally pass the `preserve_rank` argument to force abilities to appear at ranks they would normally appear at, ie. if a Confidant would normally give an ability at rank 3, they will always give a (probably) *different* ability at rank 3.

Note that some abilities have behavior that is not directly internally tied to visibly acquiring the ability, with the game using sleight of hand to make them *appear* tied. This can lead to "acquiring" some abilities that have no effect until meeting the conditions they would normally be obtained in.