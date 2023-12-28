# Overview

Python script to stream data from vicon nexus to unity. See [vicon-nexus-unity-stream](https://github.com/ovi-lab/vicon-nexus-unity-stream) for the accompanying unity package.

# Setup

## Requirements

* Python 3.8+

## Installation

Install it directly into an activated virtual environment:

```text
$ pip install vicon_nexus_unity_stream_py
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```text
$ poetry add vicon_nexus_unity_stream_py
```

# Usage

After installation, the package can be used as a cli tool:

```text
$ vicon-nexus-stream --help

Usage: vicon-nexus-stream [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  server  Connects to the vicon and streams the data...
  stream  Instead of connecting to vicon, streams data...
  test    Test if connection is working
```


# Credits
This project was generated with [cookiecutter](https://github.com/audreyr/cookiecutter) using [jacebrowning/template-python](https://github.com/jacebrowning/template-python).
