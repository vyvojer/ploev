# ploev
# Copyright (C) 2017 Alexey Londkevich <vyvojer@gmail.com>

# ploev is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ploev is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv

from abc import ABC, abstractmethod
from collections import OrderedDict


class AnkiMixin(ABC):
    def __init__(self):
        self.anki_tags = list()
        self.anki_fields = OrderedDict()

    @abstractmethod
    def fill_anki_fields(self):
        pass

    def _anki_fields_as_list(self):
        return [field for field in self.anki_fields.values()]

    def save_anki(self, file, append=True):
        self.fill_anki_fields()
        if append:
            mode = 'a'
        else:
            mode = 'w'
        with open(file, mode, newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(self._anki_fields_as_list() + [" ".join(self.anki_tags)])


