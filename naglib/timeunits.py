import datetime

class TimeUnits:
    UNIT_SECOND = 1
    UNIT_MINUTE = UNIT_SECOND * 60
    UNIT_HOUR = UNIT_MINUTE * 60
    UNIT_DAY = UNIT_HOUR * 24
    UNIT_WEEK = UNIT_DAY * 7

    UNITS = {'s': (UNIT_SECOND, 'secs'),
             'm': (UNIT_MINUTE, 'mins'),
             'h': (UNIT_HOUR, 'hours'),
             'd': (UNIT_DAY, 'days'),
             'w': (UNIT_WEEK, 'weeks'),
              }

    def __init__(self, sparam='',date_time=''):
        # value is always stored as seconds
        if sparam:
            self.value = self._parse_sparam(sparam)
        elif date_time:
            dt = datetime.datetime .now() - date_time
            self.value = dt.days * (24 * 60 * 60) + dt.seconds
        else:
            self.value = 0
        self.pref_unit = self._calculate_pref_unit()
        
    def get_by_unit_key(self, s):
        if not s in self.UNITS.keys():
            print 'get_by_unit_key() bad param'
            raise SystemError, 2
        f = self.value / self.UNITS[s][0]
        return int(f)
        
    def get_plural_label(self, unit=''):
        "if no unit given, the prefered (largest where value is > 1) is used"
        if not unit:
            unit = self.pref_unit
        if not unit in self.UNITS.keys():
            print 'get_plural_label() bad param'
            raise SystemError, 2
        return self.UNITS[unit][1]
        
    def get_rounded(self):
        "Display value in pref notation."
        i = self.get_by_unit_key(self.pref_unit)
        s = self.UNITS[self.pref_unit][1]
        return '%i %s' % (self.get_by_unit_key(self.pref_unit), self.UNITS[self.pref_unit][1])
    

    def get(self):
        lst = []
        remainder = self.value 
        for c in ('w','d','h','m','s'):
            if remainder >= self.UNITS[c][0]:
                i = int(remainder / self.UNITS[c][0])
                remainder -= i * self.UNITS[c][0]
                lst.append('%i %s' % (i, self.UNITS[c][1]))
        if not lst:
            # handling zero file age
            lst = ['0 %s' % self.UNITS[c][1]]
        return ', '.join(lst)
        
    def _calculate_pref_unit(self):
        i = self.value
        unit_value = self.UNIT_SECOND
        for u in (self.UNIT_WEEK, self.UNIT_DAY, self.UNIT_HOUR, self.UNIT_MINUTE,):
            if i >= u:
                unit_value = u
                i = int(i/u)
                break
        for k in self.UNITS.keys():
            if self.UNITS[k][0] == unit_value:
                unit = k
                break
        return unit
    
    def _parse_sparam(self, param):
        try:
            int(param)
            param ='%ss' % param
        except:
            pass
        #
        # Assume last char is the unit
        #
        uc = param[-1]
        if not uc in self.UNITS.keys():
            print 'Bad unit in param: %s' % param
            raise SystemError, 2
        try:
            value = int(float(param[:-1]))
            unit = self.UNITS[uc][0]
        except:
            print 'Bad value in param: %s' % param
            raise SystemError, 2
        
        # Zero age is perfectly fine for logfiles, so removed check    
        #if value == 0:
        #    print 'Zero file age detected: %s' % param
        #    raise SystemError, 2
        
        return value * unit
    
    def __str__(self):
        return self.get()
    
    def __lt__(self, other):
        if self.value < other.value:
            return True
        return False

    def __le__(self, other):
        if self.value <= other.value:
            return True
        return False

    def __eq__(self, other):
        if self.value == other.value:
            return True
        return False
    
    def __ne__(self, other):
        if self.value != other.value:
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

if 0:
    # testing
    for i in (1,59,60,61,3599,3600,3601,86401,604861):
        print 'time:', i, 'Displayed as:', TimeUnits(i).get()
    
    if TimeUnits(65) < TimeUnits(65):
        print 'lt failed'
        sys.exit(1)    
    if TimeUnits(65) <= TimeUnits(64):
        print 'le failed'
        sys.exit(1)    
    if TimeUnits(65) == TimeUnits(7):
        print 'eq  failed'
        sys.exit(1)
    if TimeUnits(65) != TimeUnits(65):
        print 'ne failed'
        sys.exit(1)    
    if TimeUnits(32) > TimeUnits(32):
        print 'gt  failed'
        sys.exit(1)
    if TimeUnits(42) >= TimeUnits(65):
        print 'ge failed'
        sys.exit(1)    
        
        
