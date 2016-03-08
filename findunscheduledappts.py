''' '''

import csv
import re
import itertools
import Levenshtein
from fuzzywuzzy import fuzz

# TODO load from a shared calendar

def loadcsv(fname, usecols=None):
    ''' Load data from a csvfile.'''

    with open(fname, 'rb') as f:
        reader = csv.reader(f)
        if usecols == None:
            data = [row for row in reader]
        else:
            data = [[row[col] for col in sorted(usecols)] for row in reader if len(row) > 0]

    return data

def writecsv(fname, data):
    ''' Write data to a csvfile.'''

    with open(fname, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data)

class Appointment(object):
    ''' Representation of a single calendar Appointment.'''

    def __init__(self, data):
        ''' '''
        self.sp = StringProcessor()
        self.data = data

    def _build_string_similarity_set(self, usefields=None):
        ''' Create and store a set of strings from appointment data fields.'''
        if usefields:
            comparison_string = ' '.join(self.data[i] for i in usefields)
        else:
            comparison_string = ' '.join(self.data)

        comparison_string = self.sp.delete_single_characters(comparison_string)
        comparison_string = self.sp.normalize(comparison_string)
        comparison_string = self.sp.tokenize(comparison_string)
        self.comparison_set = set(comparison_string)

    def measure_similarity(self, query_set, usefields=None, epsilon=0.89,
                           metric=Levenshtein.jaro_winkler):
        ''' Measure similarity between a string set and a stringified appt field set.'''
        self.query_set = query_set
        self.epsilon = epsilon
        self._build_string_similarity_set(usefields)
        self.similarity_scores = {
            query: max({metric(query, item): item for item in self.comparison_set})
                for query in self.query_set
        }
        self.matching_query = all(score >= self.epsilon for score in self.similarity_scores.values())


class StringProcessor(object):
    ''' An object that normalizes and tokenizes strings.'''

    def delete_single_characters(self, s):
        ''' Delete single character words from a string.'''
        return re.sub(r'\b\w\b', '', s)

    def normalize(self, s, blacklist=None):
        ''' Perform string normalization.

            Replace blacklisted characters with spaces and remove extra whitespace.
        '''
        if blacklist is None:
            self.blacklist = r'\W'
        else:
            self.blacklist = blacklist
        s = re.sub(self.blacklist, ' ', s)
        s = s.strip()
        s = re.sub(r'\s{2,}', ' ', s)
        s = s.lower()
        return s

    def tokenize(self, s):
        ''' Convert a string into a list of tokens sorted lexicographically.'''
        return sorted(s.split())


def f_chainer(inputs, chain):
    ''' Apply a chain of functions to a sequence of inputs'''
    output = inputs
    for f in chain:
        output = [f(x) for x in output]
    return output


def main(sa, sa_cal, sched_appts):
    ''' '''
    sp = StringProcessor()
    f_chain = [sp.delete_single_characters, sp.normalize, sp.tokenize, set]

    # load names from sched_appts csv into list and del header
    scheduled_pts = loadcsv(sched_appts, usecols=[0])
    del scheduled_pts[0]
    # flatten list then normalize and tokenize names
    scheduled_pts = itertools.chain.from_iterable(scheduled_pts)
    scheduled_pts = f_chainer(scheduled_pts, f_chain)

    # load sa_cal csv into list and create Appointment objs for each row in sa_cal
    appointment_list = [Appointment(row) for row in loadcsv(sa_cal)]
    for pt in scheduled_pts:
        for appt in appointment_list:
            if not getattr(appt, 'matching_query', False):
                try:
                    appt.measure_similarity(pt, [3, 4])
                except IndexError:
                    appt.measure_similarity(pt, [3])
                if appt.matching_query:
                    break

    # final list is list of appts with no matching scheduled_pt
    fname = 'unscheduled_appointments_%s.csv' % sa
    writecsv(fname, (appt.data for appt in appointment_list if not appt.matching_query))


if __name__ == '__main__':
    import sys
    main(sys.argv[1], sys.argv[2], sys.argv[3])
