# LogSim

## Team members

Thomas Yam (cyy33), Maxwell Li (ml2019), Chloe Yiu (ymy23)

## Introduction

LogSim is a logic simulator software, which is capable of simulating a logic circuit specified using 
Digital Logic Layout Mapper, a logic circuit description language.

## Run the program
Run the following commands

```
git clone https://github.com/tyamcy/IIA-Logic-Simulator.git
cd IIA-Logic-Simulator
pip install -e .
pip install -r requirements.txt
cd final
```

For text-based command line user interface, run

```
python logsim.py -c <file path>
```

Currently, the graphical user interface supports both English and Traditional Chinese. 
The language is either detected automatically or specified when the program is run.

For the system language, run

```
python logsim.py <file path>
```

For English, run

```
LANG=en_GB.UTF-8 python logsim.py <file path>
```

For Traditional Chinese, run

```
LANG=zh_HK.UTF-8 python logsim.py <file path>
```


