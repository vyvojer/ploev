import re
import os
import subprocess
import time
import xmlrpc.client
import logging
import logging.config
import pyparsing as pp
from ploev.settings import CONFIG


# noinspection SqlNoDataSourceInspection


class Pql:
    _PQL_COMMON = "select {selectors} \n{from_clause}"
    logger = logging.getLogger('ppt.Pql')

    def __init__(self, odds_oracle):
        self.odds_oracle = odds_oracle

    def equity(self, players, board='', dead=''):
        self.logger.debug('Started equity')
        return self.odds_oracle.equity(players, board, dead)

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

    def hero_equity(self, hero, villains, board=None, dead=None):
        self.logger.debug('Started hero_equity')
        selector = 'avg(riverEquity(hero)) as EQ'
        from_clause = self._construct_from_clause(board=board, dead=dead, hero=hero, players=villains)
        pql = self._PQL_COMMON.format(selectors=selector, from_clause=from_clause)
        pql_result = self.odds_oracle.pql(pql)
        return pql_result.results_dict['EQ'][PqlResult.PERCENTAGE]

    def count_in_range(self, main_range, sub_ranges, board, hero='', dead=''):
        self.logger.debug('Started count_in_range')
        selector = "count(inRange(player_{},'{}'))"
        selectors = ",\n\t".join([selector.format(1, sub_range) for sub_range in sub_ranges])
        from_clause = self._construct_from_clause(board=board, dead=dead, hero=hero, players=[main_range])
        pql = self._PQL_COMMON.format(selectors=selectors, from_clause=from_clause)
        pql_result = self.odds_oracle.pql(pql)
        return [result[PqlResult.PERCENTAGE] for result in pql_result.results_list]


class OddsOracle:
    _CONFIG_FILE = 'odds_oracle.ini'
    _JAVA_CLASS_FOLDER = 'ui_jar'
    _JAVA_JAR = 'p2.jar'
    _JAVA_CLASS = 'propokertools.cli.XMLRPCServer'

    _XMLRPC = 'http://{host}:{port}/xmlrpc'

    def __init__(self, host=None, port=None, trials=None, seconds=None, threads=None,
                 syntax=None, game=None, connect=True):
        self.path = CONFIG['ODDS_ORACLE']['path']
        self.server = None
        if host is not None:
            self.host = host
        else:
            self.host = CONFIG['SERVER']['host']
        if port is not None:
            self.port = port
        else:
            self.port = CONFIG['SERVER']['port']
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
        self.client = None
        if connect:
            self.get_client()

    def get_client(self):
        def connect():
            server.PPTServer.executePQL('', 10, 1, 1)
            self.client = server
            print('Successfully connected to {}'.format(url))
            return self.client

        url = OddsOracle._XMLRPC.format(host=self.host, port=self.port)
        server = xmlrpc.client.ServerProxy(url)
        try:
            return connect()
        except ConnectionError:
            print("Connection to {} failed".format(url))
            print("Trying to run OddsOracle server")
            self.run_server()
            try:
                return connect()
            except ConnectionError as exception:
                raise ConnectionError(
                    "Connection to {} failed: \r\n{}. \r\nIs OddsOracle server running?".format(url, exception))

    def run_server(self):
        command = 'cmd /K java -cp {} {} {}'.format(self._JAVA_JAR, self._JAVA_CLASS, self.port)
        cwd = os.path.join(self.path, OddsOracle._JAVA_CLASS_FOLDER)
        self.server = subprocess.Popen(command, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(3)

    def pql(self, pql: str):
        result = self.client.PPTServer.executePQL(pql, self.trials, self.seconds, self.threads)
        logger = logging.getLogger('ppt.OddsOracle.pql')
        logger.debug('Executed PQL: \n{} \nGot result: \n{}'.format(pql, result))
        if 'ERROR' in result:
            raise ValueError("{}in PQL: \r\n{}".format(result, pql))
        return PqlResult(result)

    def equity(self, hands, board='', dead=''):
        """
        Invoke Oracle's computeEquityAuto

        Args:
            hands(list): list of hands
            board(str): board
            dead(str): dead cards

        """
        result = self.client.PPTServer.computeEquityAuto(self.game, board, dead, self.syntax, hands,
                                                         self.trials, self.seconds, self.threads)
        return self._parse_equity_result(result)

    @staticmethod
    def _parse_equity_result(result):
        equities = []
        for m in re.finditer(r"(.+) = (.+?)% (.+)\n", result):
            equities.append(round(float(m.group(2)) / 100, 3))
        return equities

    @staticmethod
    def __parse_pql_result(result):
        counts = []
        for m in re.finditer(r"COUNT (.+) = (.+?)% \(.+\)\n", result):
            counts.append(float(m.group(2)) / 100)
        return counts


class PqlResult:
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

    def __init__(self, result):
        self.results_list = []
        self.results_dict = {}
        self.trials = None
        self._parse(result)

    def _parse(self, pql_result: str):
        """ parse pql result
        Returns:

        """
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
