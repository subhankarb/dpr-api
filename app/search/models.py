# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import sqlalchemy
import json
from app.package.models import Package
from app.profile.models import Publisher


class DataPackageQuery(object):

    query = ''
    filterClass = None
    filterTerm = None

    def __init__(self, query_string):
        self.query_string = query_string
        self._parse_query_string()

    def _build_sql_query(self):

        if self.filterClass is not None:
            if self.filterClass == 'publisher':
                sql_query = Package.query.join(Publisher).filter(Publisher.name == self.filterTerm)
            else:
                raise Exception("not supported any other filter right now")
        else:
            sql_query = Package.query

        # Should thought through not working right now
        if self.query != '*':
            sql_query = sql_query.filter(Package.descriptor[('title',)]
                                         .cast(sqlalchemy.TEXT) == "{q}".format(q=self.query))

        return sql_query

    def _parse_query_string(self):
        regex = "^((.*)\\s((\\b\\w+\\b):(\\b\\w+\\b))?|([\\w+\\*]+))"
        matches = re.match(regex, self.query_string, re.M | re.I)
        if matches.group(6):
            self.query = matches.group(6)
        elif matches.group(2):
            self.query = matches.group(2)
        if matches.group(3):
            self.filterClass = matches.group(4)
            self.filterTerm = matches.group(5)

    def get_data(self):
        data_list = []
        results = self._build_sql_query().all()
        for result in results:
            data = result.__dict__
            data['descriptor'] = json.loads(data['descriptor'])
            data.pop('_sa_instance_state', None)
            data['status'] = data['status'].value
            data_list.append(data)
        return data_list
