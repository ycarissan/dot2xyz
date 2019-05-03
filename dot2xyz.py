import os
import logging
import argparse
import pydot
import math

logging.basicConfig(filename='dot2xyz.log', level=logging.DEBUG)


def processArguments():
    """Returns the arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("dotfile", help="dot file to process")
    parser.parse_args()
    args = parser.parse_args()
    return args.dotfile


def center(geom):
    """Put the barycenter of the molecule at origin"""
    xmoy = ymoy = 0
    for at in geom.keys():
        xmoy = xmoy + geom[at]["x"]
        ymoy = ymoy + geom[at]["y"]
    xmoy = xmoy / len(geom.keys())
    ymoy = ymoy / len(geom.keys())
    for at in geom.keys():
        geom[at]["x"] = geom[at]["x"] - xmoy
        geom[at]["y"] = geom[at]["y"] - ymoy


def scale(geom):
    """scale the geometry such that the first C-C bond equals a reasonable value"""
    reasonable_value = 1.4
    at0 = list(geom.keys())[0]
    (x0, y0, z0) = (geom[at0]["x"], geom[at0]["y"], geom[at0]["z"])
    at1 = list(geom.keys())[1]
    (x1, y1, z1) = (geom[at1]["x"], geom[at1]["y"], geom[at1]["z"])
    dist = math.sqrt(math.pow((x0 - x1), 2) + math.pow((y0 - y1), 2) + math.pow((z0 - z1), 2))
    scale = reasonable_value / dist
    for at in geom.keys():
        geom[at]["x"] = geom[at]["x"] * scale
        geom[at]["y"] = geom[at]["y"] * scale
        geom[at]["z"] = geom[at]["z"] * scale
    return geom


def main():
    dotfile = processArguments()
    dot_graph = pydot.graph_from_dot_file(dotfile)[0]
    geom = {}
    for node in dot_graph.get_nodes():
        "attribute 'pos' comes with double quotes"
        (x, y) = [float(a) for a in node.get('pos').replace('"', "").split(',')]
        geom[node.get_name()] = {'x': x, 'y': y, 'z': 0}
        print(node.get_name(), x, y)
    center(geom)
    scale(geom)

    print(len(geom), '\n')
    for at in geom.keys():
        print("C", geom[at]["x"], geom[at]["y"], geom[at]["z"])


if __name__ == '__main__':
    main();
