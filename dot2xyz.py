import os
import logging
import argparse
import pydot
import math
import numpy

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
    center = numpy.array([0,0,0])
    for at in geom.keys():
        center = center + geom[at]["pos"]
    center = center / len(geom.keys())
    for at in geom.keys():
        geom[at]["pos"] = geom[at]["pos"] - center


def scale(geom):
    """scale the geometry such that the first C-C bond equals a reasonable value"""
    reasonable_value = 1.4
    at0 = list(geom.keys())[0]
    p0 = geom[at0]["pos"]
    at1 = list(geom.keys())[1]
    p1 = geom[at1]["pos"]
    dist = numpy.linalg.norm(p0-p1)
    scale = reasonable_value / dist
    for at in geom.keys():
        geom[at]["pos"] = geom[at]["pos"] * scale
    return geom


def main():
    dotfile = processArguments()
    dot_graph = pydot.graph_from_dot_file(dotfile)[0]
    geom = {}
    for node in dot_graph.get_nodes():
        "attribute 'pos' comes with double quotes"
        (x, y) = [float(a) for a in node.get('pos').replace('"', "").split(',')]
        pos=numpy.array([x,y,0])
        geom[node.get_name()] = {'pos': pos}
        print(node.get_name(), pos)
    center(geom)
    scale(geom)

    print(len(geom), '\n')
    for at in geom.keys():
        print("C", geom[at]["pos"])


if __name__ == '__main__':
    main();
