"""CLI."""

import click

from ._main import main, _init_api, _init_api_static

@click.group()
def _main():
    pass


@click.command()
@click.option("-c", "--connection", default='localhost:801')
def test(connection):
    """Test if connection is working"""
    main(connection)


@click.command()
@click.option("-c", "--connection", default='localhost:801')
@click.option("-h", "--host", default='127.0.0.1')
@click.option("-p", "--port", default='5000')
@click.option("-j", "--use-json", default=False, is_flag=True)
def server(connection, host, port, use_json):
    """Connects to the vicon and streams the data out through host:port"""
    _init_api(connection=connection, host=host, port=port, use_json=use_json)


@click.command()
@click.option("-c", "--connection", default='localhost:801')
@click.option("-h", "--host", default='127.0.0.1')
@click.option("-p", "--port", default='5000')
@click.option("-f", "--file", default=None)
@click.option("-j", "--use-json", default=False, is_flag=True)
def stream(connection, host, port, file, use_json):
    """
    Instead of connecting to vicon, streams data from a csv file. The format of the file is
    the same as the one recorded by https://github.com/ahmed-shariff/vicon-nexus-unity-stream.
    """
    _init_api_static(connection=connection, host=host, port=port, input_file=file, use_json=use_json)


_main.add_command(test)
_main.add_command(server)
_main.add_command(stream)
    

if __name__ == '__main__':  # pragma: no cover
    _main()
