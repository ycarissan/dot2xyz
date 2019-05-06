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
    center = numpy.array([0, 0, 0])
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
    dist = numpy.linalg.norm(p0 - p1)
    scale = reasonable_value / dist
    for at in geom.keys():
        geom[at]["pos"] = geom[at]["pos"] * scale
    return geom


def addHydrogens(geom, dot_graph):
    """Fill the valency of sp2 carbon atoms"""
    "For each node, build the list of connected nodes"
    for node in dot_graph.get_nodes():
        connected = []
        for edge in dot_graph.get_edges():
            if (edge.get_source() == node.get_name()):
                connected.append(edge.get_destination())
            elif (edge.get_destination() == node.get_name()):
                connected.append(edge.get_source())
            geom[node.get_name()]["connected"] = connected
    "Loop again on the centers which need an extra H"
    i = 0
    for node in dot_graph.get_nodes():
        connected = geom[node.get_name()]["connected"]
        if (len(connected) < 2) or (len(connected) > 3):
            logging.error("Error center {} is connected {} times".format(node.get_name(), len(connected)))
            exit(99)
        elif (len(connected)) == 2:
            "Here we need one hydrogen"
            "We build two vectors AB and AC, add them up and"
            "the opposite of that resulting vector should be the direction of th CH bond"
            nameA = node.get_name()
            nameB = geom[nameA]["connected"][0]
            nameC = geom[nameA]["connected"][1]
            A = geom[nameA]["pos"]
            B = geom[nameB]["pos"]
            C = geom[nameC]["pos"]
            "AB = B-A"
            "AC = C-A"
            "AB+AC = B+C-2A"
            vect = - (B + C - 2 * A)
            "we normalize and adjust the CH distance to a reasonable value"
            vect = 1.1 * vect / numpy.linalg.norm(vect)
            "we add the hydrogen"
            i = i + 1
            geom["H" + str(i)] = {'pos': A + vect, 'type': "H"}


def main():
    dotfile = processArguments()
    dot_graph = pydot.graph_from_dot_file(dotfile)[0]
    geom = {}
    for node in dot_graph.get_nodes():
        "attribute 'pos' comes with double quotes"
        (x, y) = [float(a) for a in node.get('pos').replace('"', "").split(',')]
        pos = numpy.array([x, y, 0])
        geom[node.get_name()] = {'pos': pos, 'type': "C"}
        print(node.get_name(), pos)
    center(geom)
    scale(geom)
    addHydrogens(geom, dot_graph)

    print(len(geom), '\n', file=open("geom.xyz", "w"))
    for at in geom.keys():
        print("{0} {1[0]:16.8f} {1[1]:16.8f} {1[2]:16.8f} ".format(geom[at]["type"], geom[at]["pos"]),
              file=open("geom.xyz", "a"))


if __name__ == '__main__':
    main()
