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

""" Classes for working with Odds Oracle and PQL"""

import re
import os
import functools
import subprocess
import time
import xmlrpc.client
import logging
import pyparsing as pp
from ploev.settings import CONFIG
from typing import Iterable

# noinspection SqlNoDataSourceInspection


class OddsOracle:
    """Represent OddsOracle xmlrpc server

    Attributes:
        trials (int): max trials for query
        seconds(int): max seconds for query
        threads (int): number of threads
        syntax (str): query syntax
        game: (str): game query

    """
    _CONFIG_FILE = 'odds_oracle.ini'
    _JAVA_CLASS_FOLDER = 'ui_jar'
    _JAVA_JAR = 'p2.jar'
    _JAVA_CLASS = 'propokertools.cli.XMLRPCServer'

    _XMLRPC = 'http://{host}:{port}/xmlrpc'

    logger = logging.getLogger('ppt')

    def __init__(self, host: str = None, port: str = None,
                 trials: int = None, seconds: int = None, threads: int = None,
                 syntax: str = None, game: str = None, connect: bool = True):
        """
        Arguments host, port, trials, secondd, threads, syntax, game takes from settings file if not provided

        Args:
            host (str): host of xmlrpc server
            port (str): port of xmlrpc server
            trials (int): max trials for query
            seconds (int): max seconds for query
            threads (int): number of threads
            syntax (str): query syntax
            game (str): game query
            connect (bool): tries to run and connect OddsOracle if True
        """

        self.path = CONFIG['ODDS_ORACLE']['path']
        self.server = None
        if host is not None:
            self._host = host
        else:
            self._host = CONFIG['SERVER']['host']
        if port is not None:
            self._port = port
        else:
            self._port = CONFIG['SERVER']['port']
        if trials is not None:
            self.trials = trials
        else:
            self.trials = int(CONFIG['PQL']['trials'])
        if seconds is not None:
            self.seconds = seconds
        else:
            self.seconds = int(CONFIG['PQL']['seconds'])
        if threads is not None:
            self.threads = threads
        else:
            self.threads = int(CONFIG['PQL']['threads'])
        if syntax is not None:
            self.syntax = syntax
        else:
            self.syntax = CONFIG['PQL']['syntax']
        if game is not None:
            self.game = game
        else:
            self.game = CONFIG['PQL']['game']
        self._client = None
        if connect:
            self.get_client()

    def get_client(self):
        """ Return xmlrpc client of OddsOracle

        Returns:
            xmlrpc.client.ServerProxy

        Raises:
            ConnectionError: if can't connect to server
        """

        def connect():
            server.PPTServer.executePQL('', 10, 1, 1)
            self._client = server
            self.logger.info('Successfully connected to {}'.format(url))
            return self._client

        url = OddsOracle._XMLRPC.format(host=self._host, port=self._port)
        server = xmlrpc.client.ServerProxy(url)
        try:
            return connect()
        except ConnectionError:
            self.logger.warning("Connection to {} failed".format(url))
            self.logger.info("Trying to run OddsOracle server")
            self.run_server()
            try:
                return connect()
            except ConnectionError as exception:
                raise ConnectionError(
                    "Connection to {} failed: \r\n{}. \r\nIs OddsOracle server running?".format(url, exception))

    def run_server(self):
        """ Tries to run OddsOracle server """
        command = 'cmd /K java  -Duser.language=en-US -cp {} {} {}'.format(self._JAVA_JAR, self._JAVA_CLASS, self._port)
        cwd = os.path.join(self.path, OddsOracle._JAVA_CLASS_FOLDER)
        self.server = subprocess.Popen(command, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(6)

    @functools.lru_cache()
    def pql(self, pql: str):
        """
        Invoke OddsOracle's executePQL

        Args:
            pql (str): PQL query

        Returns:
            PqlResult: result of query

        """
        result = self._client.PPTServer.executePQL(pql, self.trials, self.seconds, self.threads)
        logger = logging.getLogger('ppt.OddsOracle.pql')
        logger.info('Really executed PQL: \n{} \nGot result: \n{}'.format(pql, result))
        if 'ERROR' in result:
            raise ValueError("{}in PQL: \r\n{}".format(result, pql))
        return PqlResult(result)

    @functools.lru_cache(typed=True)
    def equity(self, hands: tuple, board: str = '', dead: str = '') -> list:
        """
        Invoke OddsOracle's computeEquityAuto

        Args:
            hands(list): list of hands
            board(str): board
            dead(str): dead cards

        Returns:
            list: list of equities

        """
        self.logger.debug(f'Really calculated (not cashed)')
        result = self._client.PPTServer.computeEquityAuto(self.game, board, dead, self.syntax, hands,
                                                          self.trials, self.seconds, self.threads)
        if 'Error' in result:
            raise ValueError(
                "{} in computeEquityAuto: \r\nboard={} dead={} hands={}".format(result, board, dead, hands))
        return self._parse_equity_result(result)

    @staticmethod
    def _parse_equity_result(result: str) -> list:
        equities = []
        for m in re.finditer(r"(.+) = (.+?)% (.+)\n", result):
            equities.append(round(float(m.group(2)) / 100, 3))
        return equities


class PqlResult:
    """ Class parsing  a pql result

    Attributes:
        results_list (list): list of parsed results
        results_dict (dict): dict of parsed results
    """
    NAME = 'name'
    PERCENTAGE = 'percentage'
    COUNTS = 'counts'
    HISTOGRAM = 'histogram'
    FRACTION = 'fraction'
    PERCENT = 'percent'

    _COUNT_SELECTOR = 'count_selector'
    _AVG_SELECTOR = 'avg_selector'
    _HISTOGRAM_SELECTOR = 'histogram_percent_selector'
    _HISTOGRAM_ELEMENT = 'histogram_percent_element'
    _TRIALS_GROUP = 'trials_group'
    _TRIALS = 'trials'

    def __init__(self, result: str):
        self.results_list = []
        self.results_dict = {}
        self.trials = None
        self._parse(result)

    def _parse(self, pql_result: str):
        """ Parses pql result """
        name = pp.Word(pp.alphanums + "_" + " ").setResultsName(self.NAME)
        percentage = pp.Word(pp.nums + '.').setResultsName(self.PERCENTAGE) + "%"
        counts = "(" + pp.Word(pp.nums).setResultsName(self.COUNTS) + ")"
        count_selector = pp.Group(name + "=" + percentage + counts).setResultsName(self._COUNT_SELECTOR)
        # avg selector
        avg_selector = pp.Group(name + "=" + pp.Word(pp.nums + '.').setResultsName(self.PERCENTAGE)).setResultsName(
            self._AVG_SELECTOR)
        # histogram_selector
        percents = [str(percent) for percent in range(100)]
        percent = pp.oneOf(percents).setResultsName(self.PERCENT)
        fraction = pp.Word(pp.nums + '/').setResultsName(self.FRACTION)
        histogram_element = pp.Group('[' + (percent ^ fraction) + ':' + percentage + counts + ']'
                                     + pp.ZeroOrMore(',')).setResultsName(self._HISTOGRAM_ELEMENT)
        histogram_selector = pp.Group(name + '=' + pp.OneOrMore(histogram_element)).setResultsName(
            self._HISTOGRAM_SELECTOR)
        # trials
        trials = pp.Group(pp.Word(pp.nums).setResultsName(self._TRIALS) + "trials").setResultsName(self._TRIALS_GROUP)
        pql_answer = pp.OneOrMore(count_selector ^ avg_selector ^ histogram_selector ^ trials)
        results = pql_answer.parseString(pql_result, parseAll=False)
        for result in results:
            if result.getName() == self._TRIALS_GROUP:
                self.trials = int(result.asDict()[self._TRIALS])
            if result.getName() in [self._COUNT_SELECTOR, self._AVG_SELECTOR, self._HISTOGRAM_SELECTOR]:
                r_d = result.asDict()
                selector_result = dict()
                name = r_d[self.NAME].rstrip()
                selector_result[self.NAME] = name
                if result.getName() == self._COUNT_SELECTOR:
                    selector_result[self.PERCENTAGE] = round(float(r_d[self.PERCENTAGE]) / 100, 3)
                    selector_result[self.COUNTS] = int(r_d[self.COUNTS])
                elif result.getName() == self._AVG_SELECTOR:
                    selector_result[self.PERCENTAGE] = round(float(r_d[self.PERCENTAGE]), 3)
                elif result.getName() == self._HISTOGRAM_SELECTOR:
                    elements = {}
                    it_was_fractions = False
                    for sub_result in result:
                        if isinstance(sub_result, pp.ParseResults):
                            sr_d = sub_result.asDict()
                            f_or_p = sr_d.get(self.FRACTION)
                            if f_or_p:
                                it_was_fractions = True
                            else:
                                f_or_p = sr_d[self.PERCENT]
                            elements[f_or_p] = {}
                            elements[f_or_p][self.PERCENTAGE] = round(float(sr_d[self.PERCENTAGE]) / 100, 3)
                            elements[f_or_p][self.COUNTS] = int(sr_d[self.COUNTS])
                    selector_result[self.HISTOGRAM] = elements
                self.results_list.append(selector_result)
                self.results_dict[name] = selector_result


class Pql:
    """ Class implements different usable PQL queries"""
    _PQL_COMMON = "select {selectors} \n{from_clause}"
    logger = logging.getLogger('ppt.Pql')

    def __init__(self, odds_oracle: OddsOracle):
        """
        Args:
            odds_oracle (OddsOracle): connected OddsOracle
        """
        self.odds_oracle = odds_oracle

    def equity(self, players: Iterable, board='', dead='') -> list:
        """ Return equities for each players.

        Args:
            players (list): list of players ranges
            board (str): board
            dead (str): dead cards

        Returns:
            list: list of equities

        """
        self.logger.debug(f'Equity will calculated (or will get from the cash) for players={players}, board={board}')
        return self.odds_oracle.equity(tuple(players), board, dead)

    def _construct_from_clause(self, board=None, dead=None, hero=None, players=None):
        from_clause = list()
        from_clause.append("from game='{}', syntax='{}'".format(self.odds_oracle.game, self.odds_oracle.syntax))
        if board:
            from_clause.append("\tboard='{}'".format(board))
        if dead:
            from_clause.append("\tdead='{}'".format(dead))
        if hero:
            from_clause.append("\thero='{}'".format(hero))
        for number, player in enumerate(players, start=1):
            from_clause.append("\tplayer_{}='{}'".format(number, player))
        return ",\n".join(from_clause)

    def hero_equity(self, hero: str, villains: list, board: str = None, dead: str = None) -> float:
        """ Return equity only for hero

        This method is faster than Pql.equity. Use Pql.equity if you need villain's equities

        Args:
            hero (str): hero's hand
            villains (list): list of villain's hand
            board (str): board
            dead (str): dead cards

        Returns:
            float: hero's equity
        """
        self.logger.debug('Started hero_equity')
        selector = 'avg(riverEquity(hero)) as EQ'
        from_clause = self._construct_from_clause(board=board, dead=dead, hero=hero, players=villains)
        pql = self._PQL_COMMON.format(selectors=selector, from_clause=from_clause)
        pql_result = self.odds_oracle.pql(pql)
        return pql_result.results_dict['EQ'][PqlResult.PERCENTAGE]

    def count_in_range(self, main_range: str, sub_ranges: list, board: str, players: Iterable[str] = None, dead: str = ''):
        """ Returns how often sub_ranges are in main_range

        Args:
            main_range (str): main range
            sub_ranges (list): sub ranges
            board (str): board
            players (Iterable[str]): Iterable of ranges of other players in the hand
            dead (str): dead cards

        Returns:
            list: list of percentages(float)

        """
        self.logger.debug('Started count_in_range')
        other_players = [main_range]
        if players is not None:
            other_players.extend(list(players))
        selector = "count(inRange(player_{},'{}'))"
        selectors = ",\n\t".join([selector.format(1, sub_range) for sub_range in sub_ranges])
        from_clause = self._construct_from_clause(board=board, dead=dead, players=other_players)
        pql = self._PQL_COMMON.format(selectors=selectors, from_clause=from_clause)
        pql_result = self.odds_oracle.pql(pql)
        return [result[PqlResult.PERCENTAGE] for result in pql_result.results_list]
