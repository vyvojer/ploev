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
from typing import Iterable, Union
from abc import ABC, abstractmethod


class Anki(ABC):
    def __init__(self):
        self.anki_description = None
        self.anki_tags = list()

    def anki_fields(self):
        return [self.anki_title(), self.anki_question(), self.anki_answer()]

    def anki_title(self):
        return self.anki_description

    @abstractmethod
    def anki_question(self):
        pass

    @abstractmethod
    def anki_answer(self):
        pass


def to_anki(file, card_object=None, card_objects=None, append=False):
    if append:
        mode = 'a'
    else:
        mode = 'w'
    if card_object:
        card_objects = [card_object]
    with open(file, mode, newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for card_object in card_objects:
            writer.writerow(card_object.anki_fields() + [" ".join(card_object.anki_tags)])

