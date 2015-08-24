# Simple-Planar-Coil-Generator
A simple square spiral planar coil generator script for kicad pcbnew footprints

## Requirements:
* Python 2.6 (or later)
* numpy

## Usage:
    $ python SquareCoilMaker.py
Outputs a single layer coil using default values.
Add the flag "-h" to get more info about user selectable parameters.

```python SquareCoilMaker.py -h
usage: SquareCoilMaker.py [-h] [-d SIDES] [-lw LINEWIDTH] [-sp SPACING]
                          [-x WIDTH] [-y HEIGHT] [-via VIASIZE]
                          [-drill DRILLSIZE] [-name COMPONENTNAME]
                          [-N NUMBEROFTURNS] [--inductance [INDUCTANCE]]
                          [-t THICKNESS]

Generates single or double sided board coils for use in kicad as footprints.
PS! The use of pad for via is yet untested. And the inductance calculation is
rough at best

optional arguments:
  -h, --help            show this help message and exit
  -d SIDES              Number of layers used for coil, (max=2), default=1
  -lw LINEWIDTH         Linewidth, default=0.25
  -sp SPACING           spacing, default=0.25
  -x WIDTH, --width WIDTH
                        width (mm), default=10
  -y HEIGHT, --height HEIGHT
                        height (mm), default=20
  -via VIASIZE          via diameter size (mm), default=0.4
  -drill DRILLSIZE      drill diameter size (mm), default=0.3
  -name COMPONENTNAME   Component name, default='Coil'
  -N NUMBEROFTURNS      Number of turns, default=7
  --inductance [INDUCTANCE]
                        (Experimental)To output an rough estimation of
                        inductance set this flag
  -t THICKNESS          Pcb thickness (mm), used in experimental inductance
                        calculations, default=1
```

## Note of warning:
The double sided coil layout have not been tested, the pad acting as a via may cause problems in your design.
And the inductance calculations are rough at best.

## Reference:
   Induction equations from: http://www.edn.com/design/components-and-packaging/4363548/A-new-calculation-for-designing-multilayer-planar-spiral-inductors