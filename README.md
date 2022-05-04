# Hegic Simulation

Simulation of the Hegic Options Platform.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependent packages.

```bash
pip install pandas
```

```bash
pip install cryptocompare
```

## Run

```bash
python sim.py
```

## Configurations

```python
amount = 1 # line 152, this can be changed if you want a different ETH amount for the option
period = 7 # line 153, this can be changed if you want a different period for the option
x = r.randint(0,1) # line 155, this can be changed if you want to set the option to 
		  # either a call (0) or a put (1)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)