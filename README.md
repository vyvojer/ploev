ploev
======

Python library for [PokerProTools Odds Oracle](http://www.propokertools.com/odds_oracle)

Quickstart
------

### Install
```
pip install ploev
```

### Usage
```python
from ploev.calc import *
odds_oracle = OddsOracle()
calc = Calc(odds_oracle)
calc.equity(players=['AcAd7h2c', 'JdTs9s8d'])
```
[0.531, 0.469]

```python
from ploev.easy_range import *
be = BoardExplorer.from_str('Ah2c7h')
be.ppt('T2P+')
```
'(AA,77,22,A7)'

```python
from ploev.easy_range import *
from ploev.calc import *
odds_oracle = OddsOracle()
calc = Calc(odds_oracle)
board = 'Ah2c3c'
be = BoardExplorer.from_str(board)
hero = 'AcAd7c2d'
villain = be.ppt('NFD:TB2P+, Str1')
calc.equity(players=[hero, villain], board=board)
```
[0.593, 0.407]

