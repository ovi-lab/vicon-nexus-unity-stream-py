"""CLI."""

import click

from vicon_nexus_unity_stream_py._main import start_server, test_connection


@click.group()
def cli():
    pass


@cli.command()
@click.option("-c", "--connection", default='localhost:801')
def test(connection):
    """Test if connection is working"""
    test_connection(connection)


@cli.command()
@click.option("-c", "--connection", default='localhost:801')
@click.option("-h", "--host", default='127.0.0.1')
@click.option("-p", "--port", default='5000')
def server(connection, host, port):
    """Connects to the vicon and streams the data out through host:port"""
    start_server(connection=connection, host=host, port=port)


# TODO: revist offline data processing
# @cli.command()
# @click.option("-c", "--connection", default='localhost:801')
# @click.option("-h", "--host", default='127.0.0.1')
# @click.option("-p", "--port", default='5000')
# @click.option("-f", "--file", default=None)
# @click.option("-j", "--use-json", default=False, is_flag=True)
# def stream(connection, host, port, file, use_json):
#     """
#     Instead of connecting to vicon, streams data from a csv file. The format of the file is
#     the same as the one recorded by https://github.com/ahmed-shariff/vicon-nexus-unity-stream.
#     """
#     _init_api_static(connection=connection, host=host, port=port, input_file=file, use_json=use_json)


if __name__ == '__main__':  # pragma: no cover
    cli()
