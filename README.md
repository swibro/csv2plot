## csv2plot

### Setup:
For now just clone repo and put something like this in .bashrc/.zshrc

This is mine for .zshrc
```
csv2plot() {
  if [[ $# -lt 1 ]]; then
    echo "Error: no CSV file provided"
    echo "Usage: csv2plot file.csv"
    return 1
  fi
  if [[ "$1" == "-e" ]]; then
    vim /path/to/plot\_proj/config.toml
  else
    python3 /path/to/plot\_proj/csv2plot.py "$1"
  fi
}
```


### Usage:
csv2plot \<file.csv\>
csv2plot -e - open config

*This usage is defined based on the setup function above
