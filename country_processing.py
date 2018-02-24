#!/usr/bin/env python3

import csv
import re
from itertools import chain
import sys
import uuid
from collections import Counter
import argparse
import os.path
import os
import warnings
import common_utils as cu
import matplotlib.cbook
warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

try:
    import geocoder
except ImportError:
    print("[ERROR] Unable to import Geocoder module: cant'run! Exit...")
    sys.exit()
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("[ERROR] Unable to import MatPlotLib module! Exit...")
    sys.exit()


class CountryProcessor():

    def __init__(self):
        self._status = ""

    def clean_name(self, tweet):
        return ' '.join(
            re.sub(
                "(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)",
                " ",
                tweet).split())

    def parse_countries(self, fname, fout):
        self._fname = fname
        self._fout = fout
        self._data = []
        self._cmap = {}
        self._cnt = 1

        self._f_writer = cu.FastWriter()

        if os.name == "nt":
            with open(fname, 'r', encoding='utf-8') as self._myFile:
                self._reader = csv.reader(self._myFile, delimiter=',')
                next(self._reader, None)
                self._myList = list(
                    self.clean_name(
                        self._i[1]) for self._i in self._reader)
        else:
            with open(fname, 'r') as self._myFile:
                self._reader = csv.reader(self._myFile, delimiter=',')
                next(self._reader, None)
                self._myList = list(
                    self.clean_name(
                        self._i[1]) for self._i in self._reader)

        try:
            print("[NOTICE] Using Komoot Geolocator Database")
            for self._location in self._myList:
                self._country_elem = geocoder.komoot(self._location)
                self._country_name = self._country_elem.country
                if self._country_name is None:
                    pass
                else:
                    print("[" + str(self._cnt) + "] " + self._country_name)
                    self._data.append(self._country_name)
                    self._cnt += 1

            self._res = dict(Counter(self._data))

            self._f_writer.fast_writer(
                self._fout,
                self._res,
                str(os.name)
                )

        except KeyboardInterrupt:
            print("[NOTICE] Interrupted. (Ctrl+C)")

            self._res = dict(Counter(self._data))

            self._f_writer.fast_writer(
                self._fout,
                self._res,
                str(os.name)
                )

    def plot_graph(self, fname, limit, num, bhash, gfile):
        self._base_hash = bhash
        self._data_file = fname
        self._limit = int(limit)
        self._num = str(num)
        self._gfile = gfile

        self._title = "Countries Analysis for " + self._num + \
            " tweets including '" + self._base_hash + "' "
        self._title += "hashtag \n(frequency over " + str(self._limit)
        self._title += ") "

        self._outfile = open(self._data_file, "r")
        self._rfile = csv.reader(self._outfile)

        self._countries = []
        self._freq = []

        for self._row in self._rfile:
            if int(self._row[1]) > self._limit:
                try:
                    self._countries.append(self._row[0])
                    self._freq.append(int(self._row[1]))
                except TypeError:
                    pass

        plt.title(self._title)
        plt.pie(
            self._freq,
            labels=self._countries,
            autopct='%1.0f%%',
            pctdistance=1.1,
            labeldistance=1.2)
        plt.axes().set_aspect('equal')
        plt.savefig(self._gfile)
        plt.show()


def get_args():
    _parser = argparse.ArgumentParser(
        description='Script plot countries pie graph from tweets dataset')
    _parser.add_argument(
        '-i',
        '--ifile',
        type=str,
        help='CSV input filename',
        required=True)
    _parser.add_argument(
        '-n',
        '--tnum',
        type=int,
        help='Number of tweets to get',
        required=True,
        default=500)
    _parser.add_argument(
        '-t',
        '--hashtag',
        type=str,
        help='Hashtag to search',
        required=True)
    _parser.add_argument(
        '-l',
        '--limitf',
        type=int,
        help='Limit hasht. frequency for plotter',
        required=False,
        default=50)

    _args = _parser.parse_args()
    _ifile = _args.ifile
    _num = int(_args.tnum)
    _hashtag = _args.hashtag
    _limit = int(_args.limitf)
    _fout = ((str(_ifile))[:-4]) + "_countries.csv"

    return _ifile, _num, _hashtag, _limit, _fout


if __name__ == "__main__":

    try:
        _ifile, _num, _hashtag, _limit, _outfile = get_args()
        print("[INFO] Tweet's Countries Analyzing Tool\n")

        _gfile = ((str(_ifile))[:-4]) + "_countries.png"

        if os.path.exists(_ifile) is False:
            print("[ERROR] Input file doesn't exists! Exit...")
            sys.exit()

        _plotter = CountryProcessor()

        if os.name != "nt":
            _f_path = "./" + _outfile
        else:
            _f_path = _outfile

        if os.path.exists(_f_path) is True:
            _plotter.plot_graph(_outfile, _limit, _num, _hashtag, _gfile)
        else:
            print("[NOTICE] Parsing countries data...")
            print("[*] Please, wait...")
            _plotter.parse_countries(_ifile, _outfile)
            _plotter.plot_graph(_outfile, _limit, _num, _hashtag, _gfile)

    except KeyboardInterrupt:
        print("[NOTICE] Script interrupted via keyboard (Ctrl+C)")
        print("Exit...")
