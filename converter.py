#!/usr/bin/env python

import os
import tempfile

from argparse import ArgumentParser
from cairosvg import svg2png
import xml.etree.ElementTree as ET

def main():
    args = parse_args()
    set_dir(args)
    try:
        check_for_svgs(args)
        set_output_dir(args)
        if args.file:
            convert_file(args)
        else:
            convert_directory(args)
    except FileNotFoundError as err:
        print('Error:', err)

def check_for_svgs(args):
    if args.file:
        if args.file.endswith(".svg"):
            pass
        else:
            raise FileNotFoundError('File is not an SVG')
    elif any(File.endswith(".svg") for File in os.listdir(args.dir)):
        pass
    else:
        raise FileNotFoundError('Directory does not contain SVGs')

def set_dir(args):
    if args.dir and not args.dir == 'here':
        os.chdir(args.dir)
    elif args.rdir:
        args.dir = os.path.join(os.getcwd(), args.rdir)
        os.chdir(args.dir)
    elif args.file:
        args.dir = os.path.split(os.path.abspath(args.file))[0]
        os.chdir(args.dir)
    else:
        args.dir = os.getcwd()
    print('Working within:', os.getcwd())

def set_output_dir(args):
    if args.rdirout:
        args.dirout = os.path.join(os.getcwd() + args.rdirout)
    if not args.dirout:
        args.dirout = os.path.join(os.getcwd() + '/png/')
    if not os.path.exists(args.dirout):
        os.makedirs(args.dirout)
    print('Outputting to:', args.dirout)

def convert_directory(args):
    for filename in os.listdir(args.dir):
        if filename.endswith(".svg"):
            args.file = filename
            convert_file(args)

def convert_file(args):
    path, filename = os.path.split(args.file)
    new_name = os.path.splitext(filename)[0]
    new_ext = '-Color-Converted.svg' if args.coloronly else '.png'
    output = new_name + new_ext

    if args.color:
        convert_color(args, output)
    else:
        with open(args.file, 'rb') as file_in, open(output, 'wb') as file_out:
            svg2png(file_in.read(), write_to=file_out)

    os.rename(os.path.join(args.dir, output), os.path.join(args.dirout, output))
    print('{} converted to {}'.format(os.path.split(args.file)[1], os.path.split(output)[1]))

def convert_color(args, output):
    with open(args.file,'r+b') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        for child in root:
            child.set('fill', args.color)
        if args.coloronly:
            tree.write(output)
        else:
            with tempfile.NamedTemporaryFile() as temp:
                tree.write(temp)
                with open(output, 'wb') as file_out:
                    svg2png(file_obj=temp, write_to=file_out)

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-w', '--width', type=int, help="Target size to render.")
    parser.add_argument('-c', '--color', help="String representation of color for fill")
    parser.add_argument('-co', '--coloronly', nargs='?', const="True", help="Only convert color")
    group_dir = parser.add_mutually_exclusive_group()
    parser.add_argument('-do', '--dirout', help="Destination directory, absolute path to directory" )
    parser.add_argument('-rdo', '--rdirout', help="Destination directory, relative to current working directory" )
    group_in = parser.add_mutually_exclusive_group()
    group_in.add_argument('-f', '--file', help="SVG file to convert")
    group_in.add_argument('-d', '--dir', nargs='?', const='here', help="Directory with SVGs")
    group_in.add_argument('-rd', '--rdir', help="Relative directory with SVGs")
    return parser.parse_args()

if __name__ == '__main__':
    main()
