# LogSim

## Team members

Thomas Yam (cyy33), Maxwell Li (ml2019), Chloe Yiu (ymy23)

## Introduction

LogSim is a logic simulator software, which is capable of simulating a logic circuit specified using 
Digital Logic Layout Mapper, a logic circuit description language.

## Run the program
Make sure the following dependencies are installed
- [wxPython](https://wiki.wxpython.org/How%20to%20install%20wxPython)
- [PyOpenGL](https://pyopengl.sourceforge.net/documentation/installation.html)
- [pytest](https://docs.pytest.org/en/7.1.x/getting-started.html)

Run the following commands

```
git clone https://github.com/tyamcy/IIA-Logic-Simulator.git
pip install -e .
cd IIA-Logic-Simulator/final
```

For text-based command line user interface, run

```
python main.py -c <file path>
```

Currently, the graphical user interface supports both English and Traditional Chinese. 
The language is either detected automatically or specified when the program is run.

For the system language, run

```
python main.py <file path>
```

For English, run

```
LANG=en_US python main.py <file path>
```

For Traditional Chinese, run

```
LANG=zh_HK python main.py <file path>
```


