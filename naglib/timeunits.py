import datetime


class TimeUnits(object):
    UNIT_SECOND = 1
    UNIT_MINUTE = UNIT_SECOND * 60
    UNIT_HOUR = UNIT_MINUTE * 60
    UNIT_DAY = UNIT_HOUR * 24
    UNIT_WEEK = UNIT_DAY * 7

    UNITS = {'s': (UNIT_SECOND, 'secs'),
             'm': (UNIT_MINUTE, 'mins'),
             'h': (UNIT_HOUR, 'hours'),
             'd': (UNIT_DAY, 'days'),
             'w': (UNIT_WEEK, 'weeks'), }

    def __init__(self, sparam=None, date_time=None):
        """sparam should be int (seconds) or string, single unit with a suffix as above"""
        # value is always stored as seconds
        if sparam:
            self.value = self._parse_sparam(sparam)
        elif date_time:
            if not isinstance(date_time, datetime.datetime):
                raise TypeError('date_time should be of type datetime.datetime')
            t1 = datetime.datetime.now()
            dt = t1 - date_time
            self.value = dt.days * (24 * 60 * 60) + dt.seconds
        else:
            self.value = 0
        if self.value < 0:
            raise ValueError('times can not be negative')
        self.pref_unit = self._calculate_pref_unit()

    def get_by_unit_key(self, s):
        if s not in self.UNITS:
            raise SystemError('get_by_unit_key() bad param')
        f = self.value / self.UNITS[s][0]
        return int(f)

    def get_plural_label(self, unit=''):
        """if no unit given, the prefered (largest where value is > 1) is used"""
        if not unit:
            unit = self.pref_unit
        if unit not in self.UNITS:
            raise SystemError('get_plural_label() bad param')
        return self.UNITS[unit][1]

    def get_rounded_down(self):
        """Display value in pref notation."""
        return '%i %s' % (self.get_by_unit_key(self.pref_unit), self.UNITS[self.pref_unit][1])

    def get(self):
        lst = []
        remainder = self.value
        c = 'w'
        for c in ('w', 'd', 'h', 'm', 's'):
            if remainder >= self.UNITS[c][0]:
                i2 = int(remainder / self.UNITS[c][0])
                remainder -= i2 * self.UNITS[c][0]
                lst.append('%i %s' % (i2, self.UNITS[c][1]))
        if not lst:
            # handling zero file age
            lst = ['0 %s' % self.UNITS[c][1]]
        return ', '.join(lst)

    def _calculate_pref_unit(self):
        i2 = self.value
        unit = self.UNIT_WEEK
        unit_value = self.UNIT_SECOND
        for u in (self.UNIT_WEEK, self.UNIT_DAY, self.UNIT_HOUR, self.UNIT_MINUTE,):
            if i2 >= u:
                unit_value = u
                i2 = int(i2 / u)
                break
        for k in self.UNITS.keys():
            if self.UNITS[k][0] == unit_value:
                unit = k
                break
        return unit

    def _parse_sparam(self, param):
        try:
            int(param)
            param = '%ss' % param
        except:
            if param.find(',') > -1:
                raise ValueError('multple entities detected')
            pass
        #
        # Assume last char is the unit
        #
        uc = param[-1]
        if uc not in self.UNITS.keys():
            raise ValueError('Bad unit in param: %s' % param)
        try:
            value = int(float(param[:-1]))
            unit = self.UNITS[uc][0]
        except:
            raise ValueError('Bad value in param: %s' % param)

        # Zero age is perfectly fine for logfiles, so removed check
        # if value == 0:
        #    print 'Zero file age detected: %s' % param
        #    raise SystemError, 2

        return value * unit

    def __str__(self):
        return self.get()

    def __eq__(self, other):
        if self.value == other.value:
            return True
        return False

    def __ne__(self, other):
        if self.value != other.value:
            return True
        return False

    def __lt__(self, other):
        if self.value < other.value:
            return True
        return False

    def __le__(self, other):
        if self.value <= other.value:
            return True
        return False

    def __gt__(self, other):
        if self.value > other.value:
            return True
        return False

    def __ge__(self, other):
        if self.value >= other.value:
            return True
        return False

    def __add__(self, other):
        return TimeUnits(self.value + other.value)

    def __sub__(self, other):
        return TimeUnits(self.value - other.value)
