#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  niederbayern_oberpfalz.py
#  
#  Copyright 2014 shad0w73 <shad0w73@maills.de>
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


# Usable locations (urls) (based on http://www.stwno.de/joomla/de/gastronomie/speiseplan):
# HS-DEG - TH Deggendorf
# HS-LA - HS Landshut
# UNI-P - Uni Passau
# OTH Regensburg:
#   HS-R-tag - Seybothstraße (mittags)
#   HS-R-abend - Seybothstraße (abends) (currently no data)
#   Cafeteria-Pruefening - Prüfeningerstr. (mittags) (currently no data)
# Uni Regensburg:
#   UNI-R - Mensa (mittags)
#   Cafeteria-PT - Cafeteria PT (mittags) (currently no data)
#   Cafeteria-Chemie - Cafeteria Chemie (currently no data)
#   Cafeteria-Milchbar - Cafeteria Milchbar (currently no data)
#   Cafeteria-Sammelgebaeude - Cafeteria Sammelgebäude (currently no data)
#   Cafeteria-Sport - Cafeteria Sport (currently no data)

# header:
# 1 - datum
# 2 - tag
# 3 - warengruppe
# 4 - name
# 5 - kennz
# 6 - preis
# 7 - stud
# 8 - bed
# 9 - gast

from csv import reader
from datetime import date, timedelta
from urllib.request import urlopen
from urllib.error import HTTPError
import re

from pyopenmensa.feed import LazyBuilder

def parse_url(url, today=False):
    canteen = LazyBuilder()
    legend = {
        '1':   'mit Farbstoff',
        '2':   'mit Konservierungsstoff',
        '3':   'mit Antioxidationsmittel',
        '4':   'mit Geschmacksverstärker',
        '5':   'geschwefelt',
        '6':   'geschwärzt',
        '7':   'gewachst',
        '8':   'mit Phosphat',
        '9':   'mit Süssungsmittel Saccharin',
        '10':  'mit Süssungsmittel Aspartam, enth. Phenylalaninquelle',
        '11':  'mit Süssungsmittel Cyclamat',
        '12':  'mit Süssungsmittel Acesulfam',
        '13':  'chininhaltig',
        '14':  'coffeinhaltig',
        '15':  'gentechnisch verändert',
        '16':  'enthält Sulfite',
        '17':  'enthält Phenylalanin',
        'A':   'Aktionsgericht',
        'B':   'mit ausschließlich biologisch erzeugten Rohstoffen',
        'F':   'Fisch',
        'G':   'Geflügel',
        'L':   'Lamm',
        'MSC': 'zertifizierte nachhaltige Fischerei (MSC-C-53400)',
        'MV':  'Mensa Vital',
        'R':   'Rindfleisch',
        'S':   'Schweinefleisch',
        'V':   'vegetarisch',
        'VG':  'vegan',
        'W':   'Wild'
    }
    canteen.setLegendData(legend)
    
    hg = re.compile("^HG[1-9]$")
    b = re.compile("^B[1-9]$")
    n = re.compile("^N[1-9]$")

    for w in 0, 1:
        kw = (date.today() + timedelta(weeks=w)).isocalendar()[1]
        try:
            f = urlopen('http://www.stwno.de/infomax/daten-extern/csv/%(location)s/%(isoweek)d.csv' %
                        {'location': url, 'isoweek': kw})
        except HTTPError as e:
            if e.code == 404:
                continue
            else:
                raise e
        f = f.read().decode('iso8859-1')
        
        roles = ('student', 'employee', 'others')
        
        initline = True
        mealreader = reader(f.splitlines(), delimiter=';')
        for row in mealreader:
            if initline:
                initline = False
            else:
                if row[2] == 'Suppe':
                    category = 'Suppe'
                elif hg.match(row[2]):
                    category = 'Hauptgerichte'
                elif b.match(row[2]):
                    category = 'Beilagen'
                elif n.match(row[2]):
                    category = 'Nachspeisen'
                else:
                    raise RuntimeError('Unknown category: ' + str(row[2]))
                
                mdate = row[0]
                name = row[3]
                notes = row[4]
                prices = [row[6], row[7], row[8]]
                canteen.addMeal(mdate, category,
                                (name + '(' + notes + ')'),
                                [], prices, roles)

    return canteen.toXMLFeed()
