import traceback
from typing import Any, Dict, List
from urllib.parse import urlparse

import dateparser
import requests

import demistomock as demisto
from CommonServerPython import *

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()

''' CONSTANTS '''
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
''' CLIENT CLASS '''


class Client(BaseClient):

    def test_connection(self) -> Dict[str, Any]:
        """Gets connection to CyberTotal

        :return: dict containing success status
        :rtype: ``Dict[str, Any]``
        """
        self._http_request(
            method='GET',
            headers={'Connection': 'keep-alive', 'Host': 'cybertotal.cycraft.com'},
            url_suffix=f'/account/login'
        )
        return {'status': 'success'}

    def test_get_reputaion(self) -> Dict[str, Any]:
        """Gets A IP Sample reputation using the '/_api/search/ip/basic' API endpoint

        :return: dict containing the IP Sample reputation as returned from the API
        :rtype: ``Dict[str, Any]``
        """
        cybertotal_result = self._http_request(
            method='GET',
            url_suffix=f'/_api/search/ip/basic/1.1.1.1'
        )
        if 'task_state' in cybertotal_result:
            return {'task_state': cybertotal_result['task_state'], 'message': 'this search is in progress, try again later...'}

        scan_time = str(cybertotal_result['scan_time'])
        permalink = cybertotal_result['url']
        url_path = urlparse(permalink).path
        (rp_left, rp_match, task_id) = url_path.rpartition('/')

        result = {
            "permalink": permalink,
            "resource": '1.1.1.1',
            "positive_detections": 0,
            "detection_engines": 0,
            "scan_date": dateparser.parse(scan_time).strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_id,
            "detection_ratio": "0/0"
        }

        if 'basic' not in cybertotal_result:
            result["message"] = "search success with no basic in cybertotal result"
            return result
        if 'BasicInfo' not in cybertotal_result['basic']:
            result["message"] = "search success with no BasicInfo in cybertotal result"
            return result
        positive_detections = 0
        detection_engines = 0
        if 'reputation' in cybertotal_result['basic']:
            if 'avVenders' in cybertotal_result['basic']['reputation']:
                detection_engines = len(cybertotal_result['basic']['reputation']['avVenders'])
                for avVender in cybertotal_result['basic']['reputation']['avVenders']:
                    if avVender['detected']:
                        positive_detections = positive_detections + 1
        # result = cybertotal_result['basic']['BasicInfo']
        result['positive_detections'] = positive_detections
        result['detection_engines'] = detection_engines
        result['detection_ratio'] = str(positive_detections) + '/' + str(detection_engines)
        result['message'] = 'search success'
        if 'score' in cybertotal_result['basic']:
            result['severity'] = cybertotal_result['basic']['score'].get('severity', -1)
            result['confidence'] = cybertotal_result['basic']['score'].get('confidence', -1)
            result['threat'] = cybertotal_result['basic']['score'].get('threat', '')
        return result

    def get_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Gets the IP reputation using the '/_api/search/ip/basic' API endpoint

        :type ip: ``str``
        :param ip: IP address to get the reputation for

        :return: dict containing the IP reputation as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        cybertotal_result = self._http_request(
            method='GET',
            url_suffix=f'/_api/search/ip/basic/' + ip
        )
        if 'task_state' in cybertotal_result:
            return {'task_state': cybertotal_result['task_state'], 'message': 'this search is in progress, try again later...'}

        scan_time = str(cybertotal_result['scan_time'])
        permalink = cybertotal_result['url']
        url_path = urlparse(permalink).path
        (rp_left, rp_match, task_id) = url_path.rpartition('/')

        result = {
            "permalink": permalink,
            "resource": ip,
            "positive_detections": 0,
            "detection_engines": 0,
            "scan_date": dateparser.parse(scan_time).strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_id,
            "detection_ratio": "0/0"
        }

        if 'basic' not in cybertotal_result:
            result["message"] = "search success with no basic in cybertotal result"
            return result
        if 'BasicInfo' not in cybertotal_result['basic']:
            result["message"] = "search success with no BasicInfo in cybertotal result"
            return result
        positive_detections = 0
        detection_engines = 0
        if 'reputation' in cybertotal_result['basic']:
            if 'avVenders' in cybertotal_result['basic']['reputation']:
                detection_engines = len(cybertotal_result['basic']['reputation']['avVenders'])
                for avVender in cybertotal_result['basic']['reputation']['avVenders']:
                    if avVender['detected']:
                        positive_detections = positive_detections + 1
        # result = cybertotal_result['basic']['BasicInfo']
        result['positive_detections'] = positive_detections
        result['detection_engines'] = detection_engines
        result['detection_ratio'] = str(positive_detections) + '/' + str(detection_engines)
        result['message'] = 'search success'
        if 'score' in cybertotal_result['basic']:
            result['severity'] = cybertotal_result['basic']['score'].get('severity', -1)
            result['confidence'] = cybertotal_result['basic']['score'].get('confidence', -1)
            result['threat'] = cybertotal_result['basic']['score'].get('threat', '')
        return result

    def get_url_reputation(self, url: str) -> Dict[str, Any]:
        """Gets the URL reputation using the '/_api/search/url/basic' API endpoint

        :type url: ``str``
        :param url: URL to get the reputation for

        :return: dict containing the URL reputation as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        cybertotal_result = self._http_request(
            method='GET',
            url_suffix=f'/_api/search/url/basic?q=' + url
        )
        if 'task_state' in cybertotal_result:
            return {'task_state': cybertotal_result['task_state'], 'message': 'this search is in progress, try again later...'}
        scan_time = str(cybertotal_result['scan_time'])
        permalink = cybertotal_result['url']
        url_path = urlparse(permalink).path
        (rp_left, rp_match, task_id) = url_path.rpartition('/')
        result = {
            "permalink": permalink,
            "positive_detections": 0,
            "resource": url,
            "scan_date": dateparser.parse(scan_time).strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_id,
            "detection_engines": 0,
            "detection_ratio": "0/0"
        }
        if 'basic' not in cybertotal_result:
            result["message"] = "search success with no basic in cybertotal result"
            return result
        if 'BasicInfo' not in cybertotal_result['basic']:
            result["message"] = "search success with no BasicInfo in cybertotal result"
            return result
        positive_detections = 0
        detection_engines = 0
        if 'reputation' in cybertotal_result['basic']:
            if 'avVenders' in cybertotal_result['basic']['reputation']:
                detection_engines = len(cybertotal_result['basic']['reputation']['avVenders'])
                for avVender in cybertotal_result['basic']['reputation']['avVenders']:
                    if avVender['detected']:
                        positive_detections = positive_detections + 1
        result['detection_engines'] = detection_engines
        result['positive_detections'] = positive_detections
        result['detection_ratio'] = str(positive_detections) + '/' + str(detection_engines)
        result['message'] = 'search success'
        if 'score' in cybertotal_result['basic']:
            result['severity'] = cybertotal_result['basic']['score'].get('severity', -1)
            result['confidence'] = cybertotal_result['basic']['score'].get('confidence', -1)
            result['threat'] = cybertotal_result['basic']['score'].get('threat', '')
        return result

    def get_file_reputation(self, _hash: str) -> Dict[str, Any]:
        """Gets the File reputation using the '/_api/search/hash/basic' API endpoint

        :type file: ``str``
        :param file: File to get the reputation for

        :return: dict containing the File reputation as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        cybertotal_result = self._http_request(
            method='GET',
            url_suffix=f'/_api/search/hash/basic/' + _hash
        )
        if 'task_state' in cybertotal_result:
            return {'task_state': cybertotal_result['task_state'], 'message': 'this search is in progress, try again later...'}

        scan_time = str(cybertotal_result['scan_time'])
        permalink = cybertotal_result['url']
        url_path = urlparse(permalink).path
        (rp_left, rp_match, task_id) = url_path.rpartition('/')

        result = {
            "permalink": permalink,
            "positive_detections": 0,
            "resource": _hash,
            "scan_date": dateparser.parse(scan_time).strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_id,
            "detection_engines": 0,
            "detection_ratio": "0/0"
        }
        if 'basic' not in cybertotal_result:
            result["message"] = "search success with no basic in cybertotal result"
            return result
        if 'BasicInfo' not in cybertotal_result['basic']:
            result["message"] = "search success with no BasicInfo in cybertotal result"
            return result

        basic = cybertotal_result['basic']['BasicInfo']
        result['size'] = basic.get('filesize', '')
        result['md5'] = basic.get('md5', '')
        result['sha1'] = basic.get('sha1', '')
        result['sha256'] = basic.get('sha256', '')
        result['extension'] = basic.get('file_type_extension', '')
        result['name'] = basic.get('display_name', '')
        if type(result['name']) is list:
            result['name'] = ', '.join(result['name'])

        positive_detections = 0
        detection_engines = 0
        if 'reputation' in cybertotal_result['basic']:
            if 'avVenders' in cybertotal_result['basic']['reputation']:
                detection_engines = len(cybertotal_result['basic']['reputation']['avVenders'])
                for avVender in cybertotal_result['basic']['reputation']['avVenders']:
                    if avVender['detected']:
                        positive_detections = positive_detections + 1
        result['detection_engines'] = detection_engines
        result['positive_detections'] = positive_detections
        result['detection_ratio'] = str(positive_detections) + '/' + str(detection_engines)
        result['message'] = "search success"
        if 'score' in cybertotal_result['basic']:
            result['severity'] = cybertotal_result['basic']['score'].get('severity', -1)
            result['confidence'] = cybertotal_result['basic']['score'].get('confidence', -1)
            result['threat'] = cybertotal_result['basic']['score'].get('threat', '')
        return result

    def get_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Gets the Domain reputation using the '/_api/search/domain/basic' API endpoint

        :type domain: ``str``
        :param domain: Domain to get the reputation for

        :return: dict containing the Domain reputation as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        cybertotal_result = self._http_request(
            method='GET',
            url_suffix=f'/_api/search/domain/basic/' + domain
        )
        if 'task_state' in cybertotal_result:
            return {'task_state': cybertotal_result['task_state'], 'message': 'this search is in progress, try again later...'}

        scan_time = str(cybertotal_result['scan_time'])
        permalink = cybertotal_result['url']
        url_path = urlparse(permalink).path
        (rp_left, rp_match, task_id) = url_path.rpartition('/')

        result = {
            "permalink": permalink,
            "positive_detections": 0,
            "resource": domain,
            "scan_date": dateparser.parse(scan_time).strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_id,
            "detection_engines": 0,
            "detection_ratio": "0/0"
        }
        if 'basic' not in cybertotal_result:
            result["message"] = "search success with no basic in cybertotal result"
            return result
        if 'BasicInfo' not in cybertotal_result['basic']:
            result["message"] = "search success with no BasicInfo in cybertotal result"
            return result

        positive_detections = 0
        detection_engines = 0
        if 'reputation' in cybertotal_result['basic']:
            if 'avVenders' in cybertotal_result['basic']['reputation']:
                detection_engines = len(cybertotal_result['basic']['reputation']['avVenders'])
                for avVender in cybertotal_result['basic']['reputation']['avVenders']:
                    if avVender['detected']:
                        positive_detections = positive_detections + 1
        result['detection_engines'] = detection_engines
        result['positive_detections'] = positive_detections
        result['detection_ratio'] = str(positive_detections) + '/' + str(detection_engines)
        result['message'] = "search success"
        if 'score' in cybertotal_result['basic']:
            result['severity'] = cybertotal_result['basic']['score'].get('severity', -1)
            result['confidence'] = cybertotal_result['basic']['score'].get('confidence', -1)
            result['threat'] = cybertotal_result['basic']['score'].get('threat', '')
        return result

    def get_ip_whois(self, ip: str) -> Dict[str, Any]:
        """Gets the IP-whois information using the '/_api/search/ip/whois' API endpoint

        :type ip: ``str``
        :param ip: IP address to get the whois information for

        :return: dict containing the IP whois information as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        cybertotal_result = self._http_request(
            method='GET',
            url_suffix=f'/_api/search/ip/whois/' + ip
        )
        if 'task_state' in cybertotal_result:
            return {'task_state': cybertotal_result['task_state'], 'message': 'this search is in progress, try again later...'}
        scan_time = str(cybertotal_result['scan_time'])
        permalink = cybertotal_result['url']
        url_path = urlparse(permalink).path
        (rp_left, rp_match, task_id) = url_path.rpartition('/')

        result = dict()
        if 'whois' in cybertotal_result:
            if len(cybertotal_result['whois']) > 0:
                result = cybertotal_result['whois'].pop(0)
        result['permalink'] = permalink,
        result['resource'] = ip,
        result['scan_date'] = dateparser.parse(scan_time).strftime("%Y-%m-%d %H:%M:%S"),
        result['task_id'] = task_id
        result["message"] = "search success"
        return result

    def get_url_whois(self, url: str) -> Dict[str, Any]:
        """Gets the URL-whois information using the '/_api/search/url/whois' API endpoint

        :type url: ``str``
        :param url: URL to get the whois information for

        :return: dict containing the URL whois information as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        cybertotal_result = self._http_request(
            method='GET',
            url_suffix=f'/_api/search/url/whois?q=' + url
        )
        if 'task_state' in cybertotal_result:
            return {'task_state': cybertotal_result['task_state'], 'message': 'this search is in progress, try again later...'}
        scan_time = str(cybertotal_result['scan_time'])
        permalink = cybertotal_result['url']
        url_path = urlparse(permalink).path
        (rp_left, rp_match, task_id) = url_path.rpartition('/')

        result = dict()
        if 'whois' in cybertotal_result:
            if len(cybertotal_result['whois']) > 0:
                result = cybertotal_result['whois'].pop(0)

        result['permalink'] = permalink,
        result['resource'] = url,
        result['scan_date'] = dateparser.parse(scan_time).strftime("%Y-%m-%d %H:%M:%S"),
        result['task_id'] = task_id
        result["message"] = "search success"
        return result

    def get_domain_whois(self, domain: str) -> Dict[str, Any]:
        """Gets the Domain-whois information using the '/_api/search/domain/whois' API endpoint

        :type domain: ``str``
        :param domain: Domain to get the whois information for

        :return: dict containing the Domain whois information as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        cybertotal_result = self._http_request(
            method='GET',
            url_suffix=f'/_api/search/domain/whois/' + domain
        )
        if 'task_state' in cybertotal_result:
            return {'task_state': cybertotal_result['task_state'], 'message': 'this search is in progress, try again later...'}
        scan_time = str(cybertotal_result['scan_time'])
        permalink = cybertotal_result['url']
        url_path = urlparse(permalink).path
        (rp_left, rp_match, task_id) = url_path.rpartition('/')

        result = dict()
        if 'whois' in cybertotal_result:
            if len(cybertotal_result['whois']) > 0:
                result = cybertotal_result['whois'].pop(0)

        result['permalink'] = permalink,
        result['resource'] = domain,
        result['scan_date'] = dateparser.parse(scan_time).strftime("%Y-%m-%d %H:%M:%S"),
        result['task_id'] = task_id
        result["message"] = "search success"
        return result


def test_module(client: Client) -> str:
    """Tests API connectivity and authentication'

    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :return: 'ok' if test passed, anything else will fail the test.
    :rtype: ``str``
    """

    try:
        client.test_get_reputaion()
    except DemistoException as e:
        if 'Forbidden' in str(e):
            return 'Authorization Error: make sure API Key is correctly set'
        else:
            raise e
    return 'ok'


def test_connect_cybertotal_command(client: Client) -> CommandResults:
    """test_connect_cybertotal_command command: Test if network to CyberTotal is accessable

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains the CyberTotal message

    :rtype: ``CommandResults``
    """
    result = client.test_connection()
    readable_output = f'## {result}'
    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='test_connection',
        outputs_key_field='',
        outputs=result
    )


def ip_reputation_command(client: Client, args: Dict[str, Any], default_threshold: int) -> CommandResults:
    """ip command: Returns IP reputation for a list of IPs

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['ip']`` is a list of IPs or a single IP
        ``args['threshold']`` threshold to determine whether an IP is malicious

    :type default_threshold: ``int``
    :param default_threshold:
        default threshold to determine whether an IP is malicious
        if threshold is not specified in the XSOAR arguments

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains IPs

    :rtype: ``CommandResults``
    """

    ips = argToList(args.get('ip'))
    if len(ips) == 0:
        raise ValueError('IP(s) not specified')

    threshold = int(args.get('threshold', default_threshold))

    ip_standard_list: List[Common.IP] = []
    ip_data_list: List[Dict[str, Any]] = []
    ip_message_list: List[Dict[str, Any]] = []

    for ip in ips:
        ip_data = client.get_ip_reputation(ip)
        if 'task_state' in ip_data:
            task_state = ip_data.get('task_state', 'none')
            demisto.debug(f'search this ip {ip} on cybertotal with status: {task_state}')
            ip_message_list.append({'ip': ip})
            continue

        score = 0
        reputation = int(ip_data.get('positive_detections', 0))
        if reputation == 0:
            score = Common.DBotScore.NONE  # unknown
        elif reputation >= threshold:
            score = Common.DBotScore.BAD  # bad
        elif reputation >= threshold / 2:
            score = Common.DBotScore.SUSPICIOUS  # suspicious
        else:
            score = Common.DBotScore.GOOD  # good

        dbot_score = Common.DBotScore(
            indicator=ip,
            indicator_type=DBotScoreType.IP,
            integration_name='CyberTotal',
            score=score,
            malicious_description=f'CyberTotal returned reputation {reputation}'
        )

        ip_standard_context = Common.IP(
            ip=ip,
            detection_engines=ip_data.get('detection_engines', None),
            positive_engines=ip_data.get('positive_detections', None),
            dbot_score=dbot_score
        )

        ip_standard_list.append(ip_standard_context)
        ip_data_list.append(ip_data)

    readable_output = tableToMarkdown('IP List', ip_data_list)
    if len(ip_message_list) > 0:
        readable_output += tableToMarkdown('IP search in progress , please try again later', ip_message_list)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='CyberTotal.IP',
        outputs_key_field='task_id',
        outputs=ip_data_list,
        indicators=ip_standard_list
    )


def url_reputation_command(client: Client, args: Dict[str, Any], default_threshold: int) -> CommandResults:
    """url command: Returns URL reputation for a list of URLs

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['url']`` is a list of URLs or a single URL
        ``args['threshold']`` threshold to determine whether an URL is malicious

    :type default_threshold: ``int``
    :param default_threshold:
        default threshold to determine whether an URL is malicious
        if threshold is not specified in the XSOAR arguments

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains URLs

    :rtype: ``CommandResults``
    """

    urls = argToList(args.get('url'))
    if len(urls) == 0:
        raise ValueError('URL(s) not specified')

    threshold = int(args.get('threshold', default_threshold))

    url_standard_list: List[Common.URL] = []
    url_data_list: List[Dict[str, Any]] = []
    url_message_list: List[Dict[str, Any]] = []

    for url in urls:
        url_raw_response = client.get_url_reputation(url)
        if 'task_state' in url_raw_response:
            task_state = url_raw_response.get('task_state', 'none')
            demisto.debug(f'search this url {url} on cybertotal with status: {task_state}')
            url_message_list.append({'url': url})
            continue

        reputation = int(url_raw_response.get('positive_detections', 0))
        score = Common.DBotScore.GOOD
        if reputation >= threshold:
            score = Common.DBotScore.BAD

        dbot_score = Common.DBotScore(
            indicator=url,
            indicator_type=DBotScoreType.URL,
            integration_name='CyberTotal',
            score=score,
        )

        url_standard_context = Common.URL(
            url=url,
            detection_engines=url_raw_response.get('detection_engines'),
            positive_detections=url_raw_response.get('positive_detections'),
            dbot_score=dbot_score
        )

        url_standard_list.append(url_standard_context)
        url_data_list.append(url_raw_response)

    readable_output = tableToMarkdown('URL List', url_data_list)
    if len(url_message_list) > 0:
        readable_output += tableToMarkdown('URL search in progress , please try again later', url_message_list)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='CyberTotal.URL',
        outputs_key_field='task_id',
        outputs=url_data_list,
        indicators=url_standard_list
    )


def file_reputation_command(client: Client, args: Dict[str, Any], default_threshold: int) -> CommandResults:
    """file command: Returns File reputation for a list of Files

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['file']`` is a list of Files or a single File
        ``args['threshold']`` threshold to determine whether an File is malicious

    :type default_threshold: ``int``
    :param default_threshold:
        default threshold to determine whether an File is malicious
        if threshold is not specified in the XSOAR arguments

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains Files

    :rtype: ``CommandResults``
    """

    hashs = argToList(args.get('hash'))
    if len(hashs) == 0:
        raise ValueError('HASH(s) not specified')

    threshold = int(args.get('threshold', default_threshold))

    hash_standard_list: List[Common.File] = []
    hash_data_list: List[Dict[str, Any]] = []
    hash_message_list: List[Dict[str, Any]] = []

    for _hash in hashs:
        hash_reputation_response = client.get_file_reputation(_hash)
        if 'task_state' in hash_reputation_response:
            task_state = hash_reputation_response.get('task_state', 'none')
            demisto.debug(f'search this file {_hash} on cybertotal with status: {task_state}')
            hash_message_list.append({'file': _hash})
            continue

        score = Common.DBotScore.GOOD
        reputation = int(hash_reputation_response.get('positive_detections', 0))
        if reputation > threshold:
            score = Common.DBotScore.BAD
        if reputation > 3:
            score = Common.DBotScore.SUSPICIOUS

        dbot_score = Common.DBotScore(
            indicator=_hash,
            indicator_type=DBotScoreType.FILE,
            integration_name='CyberTotal',
            score=score,
            malicious_description=f'CyberTotal returned reputation {reputation}'
        )

        hash_standard_context = Common.File(
            md5=hash_reputation_response.get('md5', None),
            sha1=hash_reputation_response.get('sha1', None),
            sha256=hash_reputation_response.get('sha256', None),
            size=hash_reputation_response.get('size', None),
            extension=hash_reputation_response.get('extension', None),
            name=hash_reputation_response.get('name', None),
            dbot_score=dbot_score
        )

        hash_standard_list.append(hash_standard_context)
        hash_data_list.append(hash_reputation_response)

    readable_output = tableToMarkdown('File List', hash_data_list)
    if len(hash_message_list) > 0:
        readable_output += tableToMarkdown('File search in progress , please try again later', hash_message_list)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='CyberTotal.File',
        outputs_key_field='task_id',
        outputs=hash_data_list,
        indicators=hash_standard_list
    )


def domain_reputation_command(client: Client, args: Dict[str, Any], default_threshold: int) -> CommandResults:
    """domain command: Returns Domain reputation for a list of Domains

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['domain']`` is a list of Domains or a single Domain
        ``args['threshold']`` threshold to determine whether an Domain is malicious

    :type default_threshold: ``int``
    :param default_threshold:
        default threshold to determine whether an Domain is malicious
        if threshold is not specified in the XSOAR arguments

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains Domains

    :rtype: ``CommandResults``
    """

    domains = argToList(args.get('domain'))
    if len(domains) == 0:
        raise ValueError('domain(s) not specified')

    threshold = int(args.get('threshold', default_threshold))

    # Context standard for Domain class
    domain_standard_list: List[Common.Domain] = []
    domain_data_list: List[Dict[str, Any]] = []
    domain_message_list: List[Dict[str, Any]] = []

    for domain in domains:
        domain_data = client.get_domain_reputation(domain)
        if 'task_state' in domain_data:
            task_state = domain_data.get('task_state', 'none')
            demisto.debug(f'search this domain {domain} on cybertotal with status: {task_state}')
            domain_message_list.append({'domain': domain})
            continue
        score = 0
        reputation = int(domain_data.get('positive_detections', 0))
        if reputation == 0:
            score = Common.DBotScore.NONE  # unknown
        elif reputation >= threshold:
            score = Common.DBotScore.BAD  # bad
        elif reputation >= threshold / 2:
            score = Common.DBotScore.SUSPICIOUS  # suspicious
        else:
            score = Common.DBotScore.GOOD  # good

        dbot_score = Common.DBotScore(
            indicator=domain,
            integration_name='CyberTotal',
            indicator_type=DBotScoreType.DOMAIN,
            score=score,
            malicious_description=f'CyberTotal returned reputation {reputation}'
        )

        domain_standard_context = Common.Domain(
            domain=domain,
            positive_detections=domain_data.get('positive_detections', None),
            detection_engines=domain_data.get('detection_engines', None),
            dbot_score=dbot_score
        )

        domain_standard_list.append(domain_standard_context)
        domain_data_list.append(domain_data)

    readable_output = tableToMarkdown('Domain List', domain_data_list)
    if len(domain_message_list) > 0:
        readable_output += tableToMarkdown('Domain search in progress , please try again later', domain_message_list)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='CyberTotal.Domain',
        outputs_key_field='task_id',
        outputs=domain_data_list,
        indicators=domain_standard_list
    )


def ip_whois_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """cybertotal-ip-whois command: Returns IP whois information for a list of IPs

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['ip']`` is a list of IPs or a single IP

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains IPs

    :rtype: ``CommandResults``
    """

    ips = argToList(args.get('ip'))
    if len(ips) == 0:
        raise ValueError('IP(s) not specified')

    ip_data_list: List[Dict[str, Any]] = []

    for ip in ips:
        ip_data = client.get_ip_whois(ip)
        ip_data_list.append(ip_data)

    return CommandResults(
        outputs_prefix='CyberTotal.WHOIS-IP',
        outputs_key_field='task_id',
        outputs=ip_data_list
    )


def url_whois_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """cybertotal-url-whois command: Returns URL whois information for a list of URLs

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['url']`` is a list of URLs or a single URL

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains URLs

    :rtype: ``CommandResults``
    """

    urls = argToList(args.get('url'))
    if len(urls) == 0:
        raise ValueError('URL(s) not specified')

    url_data_list: List[Dict[str, Any]] = []

    for url in urls:
        url_data = client.get_url_whois(url)
        url_data_list.append(url_data)

    return CommandResults(
        outputs_prefix='CyberTotal.WHOIS-URL',
        outputs_key_field='task_id',
        outputs=url_data_list
    )


def domain_whois_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """cybertotal-domain-whois command: Returns Domain whois information for a list of Domains

    :type client: ``Client``
    :param Client: CyberTotal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['domain']`` is a list of Domains or a single Domain

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains Domains

    :rtype: ``CommandResults``
    """

    domains = argToList(args.get('domain'))
    if len(domains) == 0:
        raise ValueError('Domain(s) not specified')

    domain_data_list: List[Dict[str, Any]] = []

    for domain in domains:
        domain_data = client.get_domain_whois(domain)
        domain_data_list.append(domain_data)

    return CommandResults(
        outputs_prefix='CyberTotal.WHOIS-Domain',
        outputs_key_field='task_id',
        outputs=domain_data_list
    )


def main() -> None:

    verify_certificate = not demisto.params().get('insecure', False)
    cybertotal_url = demisto.params().get('url')
    cybertotal_token = demisto.params().get('token')

    proxy = demisto.params().get('proxy', False)

    demisto.debug(f'Command being called is {demisto.command()}')
    try:
        headers = {
            'Authorization': f'Token {cybertotal_token}'
        }
        client = Client(
            base_url=cybertotal_url,
            verify=verify_certificate,
            headers=headers,
            proxy=proxy)

        if demisto.command() == 'test-module':
            # This is the call made when pressing the integration Test button.
            # result = test_module(client, first_fetch_time)
            # return_results(result)
            pass

        elif demisto.command() == 'ip':
            default_threshold = int(demisto.params().get('threshold_ip', '10'))
            return_results(ip_reputation_command(client, demisto.args(), default_threshold))

        elif demisto.command() == 'url':
            default_threshold = int(demisto.params().get('threshold_url', '10'))
            return_results(url_reputation_command(client, demisto.args(), default_threshold))

        elif demisto.command() == 'domain':
            default_threshold = int(demisto.params().get('threshold_domain', '10'))
            return_results(domain_reputation_command(client, demisto.args(), default_threshold))

        elif demisto.command() == 'file':
            default_threshold = int(demisto.params().get('threshold_hash', '10'))
            return_results(file_reputation_command(client, demisto.args(), default_threshold))

        elif demisto.command() == 'cybertotal-ip-whois':
            return_results(ip_whois_command(client, demisto.args()))

        elif demisto.command() == 'cybertotal-url-whois':
            return_results(url_whois_command(client, demisto.args()))

        elif demisto.command() == 'cybertotal-domain-whois':
            return_results(domain_whois_command(client, demisto.args()))

        # elif demisto.command() == 'whois':
        #     return_results(whois_command(client, demisto.args(), wait_inprogress_interval))
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(f'Failed to execute {demisto.command()} command.\nError:\n{str(e)}')


''' ENTRY POINT '''


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
