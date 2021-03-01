# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 Oliver Oxtoby <oliveroxtoby@gmail.com>             *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD, Part, Mesh, os, tempfile


""" 
This module provides tools to import multi-patch
ascii STL files. It is an alternative to the standard Mesh STL
importer, but supports reading multiple patches
in a single STL file
"""


# Python's open is masked by the function below
if open.__module__ in ['__builtin__','io']:
    pythonopen = open


def open(filename):
    """ Called to open a file """
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname.encode("utf8"))
    doc.Label = docname
    return insert(filename, doc.Name)


def insert(filename, docname):
    """ Called to import a file """
    try:
        doc = FreeCAD.getDocument(docname)
    except NameError:
        doc = FreeCAD.newDocument(docname)
    FreeCAD.ActiveDocument = doc

    with pythonopen(filename) as infile:
        while True:  # Keep reading solids
            solidline = infile.readline()
            if not solidline:
                break
            solidlinewords = solidline.strip().split(' ', 1)
            if solidlinewords[0] != 'solid' or len(solidlinewords) != 2:
                raise RuntimeError("Expected line of the form 'solid <name>'")
            solidname = solidlinewords[1]
            with tempfile.TemporaryDirectory() as tmpdirname:
                filename = os.path.normpath(os.path.join(tmpdirname, solidname+'.stl'))
                with pythonopen(filename, mode='w') as tmp_file:
                    tmp_file.write(solidline)
                    while True:  # Keep reading triangles
                        line = infile.readline()
                        if not line:
                            break
                        tmp_file.write(line)
                        if line.startswith('endsolid'):
                            break
                Mesh.insert(filename, docname)

    FreeCAD.Console.PrintMessage("Imported " + filename + "\n")
    return doc
