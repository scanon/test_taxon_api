#!/usr/bin/env python
from wsgiref.simple_server import make_server
import sys
import json
import traceback
import datetime
from multiprocessing import Process
from getopt import getopt, GetoptError
from jsonrpcbase import JSONRPCService, InvalidParamsError, KeywordError,\
    JSONRPCError, ServerError, InvalidRequestError
from os import environ
from ConfigParser import ConfigParser
from biokbase import log
import biokbase.nexus
import requests as _requests
import urlparse as _urlparse
import random as _random
import os
import requests.packages.urllib3

DEPLOY = 'KB_DEPLOYMENT_CONFIG'
SERVICE = 'KB_SERVICE_NAME'

# Note that the error fields do not match the 2.0 JSONRPC spec

def get_config_file():
    return environ.get(DEPLOY, None)


def get_service_name():
    return environ.get(SERVICE, None)


def get_config():
    if not get_config_file():
        return None
    retconfig = {}
    config = ConfigParser()
    config.read(get_config_file())
    for nameval in config.items(get_service_name() or 'TestTaxonAPI'):
        retconfig[nameval[0]] = nameval[1]
    return retconfig

config = get_config()

from TestTaxonAPI.TestTaxonAPIImpl import TestTaxonAPI
impl_TestTaxonAPI = TestTaxonAPI(config)


class JSONObjectEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, frozenset):
            return list(obj)
        if hasattr(obj, 'toJSONable'):
            return obj.toJSONable()
        return json.JSONEncoder.default(self, obj)

sync_methods = {}
async_run_methods = {}
async_check_methods = {}
async_run_methods['TestTaxonAPI.get_parent_async'] = ['TestTaxonAPI', 'get_parent']
async_check_methods['TestTaxonAPI.get_parent_check'] = ['TestTaxonAPI', 'get_parent']
sync_methods['TestTaxonAPI.get_parent'] = True
async_run_methods['TestTaxonAPI.get_children_async'] = ['TestTaxonAPI', 'get_children']
async_check_methods['TestTaxonAPI.get_children_check'] = ['TestTaxonAPI', 'get_children']
sync_methods['TestTaxonAPI.get_children'] = True
async_run_methods['TestTaxonAPI.get_genome_annotations_async'] = ['TestTaxonAPI', 'get_genome_annotations']
async_check_methods['TestTaxonAPI.get_genome_annotations_check'] = ['TestTaxonAPI', 'get_genome_annotations']
sync_methods['TestTaxonAPI.get_genome_annotations'] = True
async_run_methods['TestTaxonAPI.get_scientific_lineage_async'] = ['TestTaxonAPI', 'get_scientific_lineage']
async_check_methods['TestTaxonAPI.get_scientific_lineage_check'] = ['TestTaxonAPI', 'get_scientific_lineage']
sync_methods['TestTaxonAPI.get_scientific_lineage'] = True
async_run_methods['TestTaxonAPI.get_scientific_name_async'] = ['TestTaxonAPI', 'get_scientific_name']
async_check_methods['TestTaxonAPI.get_scientific_name_check'] = ['TestTaxonAPI', 'get_scientific_name']
sync_methods['TestTaxonAPI.get_scientific_name'] = True
async_run_methods['TestTaxonAPI.get_taxonomic_id_async'] = ['TestTaxonAPI', 'get_taxonomic_id']
async_check_methods['TestTaxonAPI.get_taxonomic_id_check'] = ['TestTaxonAPI', 'get_taxonomic_id']
sync_methods['TestTaxonAPI.get_taxonomic_id'] = True
async_run_methods['TestTaxonAPI.get_kingdom_async'] = ['TestTaxonAPI', 'get_kingdom']
async_check_methods['TestTaxonAPI.get_kingdom_check'] = ['TestTaxonAPI', 'get_kingdom']
sync_methods['TestTaxonAPI.get_kingdom'] = True
async_run_methods['TestTaxonAPI.get_domain_async'] = ['TestTaxonAPI', 'get_domain']
async_check_methods['TestTaxonAPI.get_domain_check'] = ['TestTaxonAPI', 'get_domain']
sync_methods['TestTaxonAPI.get_domain'] = True
async_run_methods['TestTaxonAPI.get_genetic_code_async'] = ['TestTaxonAPI', 'get_genetic_code']
async_check_methods['TestTaxonAPI.get_genetic_code_check'] = ['TestTaxonAPI', 'get_genetic_code']
sync_methods['TestTaxonAPI.get_genetic_code'] = True
async_run_methods['TestTaxonAPI.get_aliases_async'] = ['TestTaxonAPI', 'get_aliases']
async_check_methods['TestTaxonAPI.get_aliases_check'] = ['TestTaxonAPI', 'get_aliases']
sync_methods['TestTaxonAPI.get_aliases'] = True
async_run_methods['TestTaxonAPI.get_info_async'] = ['TestTaxonAPI', 'get_info']
async_check_methods['TestTaxonAPI.get_info_check'] = ['TestTaxonAPI', 'get_info']
sync_methods['TestTaxonAPI.get_info'] = True
async_run_methods['TestTaxonAPI.get_history_async'] = ['TestTaxonAPI', 'get_history']
async_check_methods['TestTaxonAPI.get_history_check'] = ['TestTaxonAPI', 'get_history']
sync_methods['TestTaxonAPI.get_history'] = True
async_run_methods['TestTaxonAPI.get_provenance_async'] = ['TestTaxonAPI', 'get_provenance']
async_check_methods['TestTaxonAPI.get_provenance_check'] = ['TestTaxonAPI', 'get_provenance']
sync_methods['TestTaxonAPI.get_provenance'] = True
async_run_methods['TestTaxonAPI.get_id_async'] = ['TestTaxonAPI', 'get_id']
async_check_methods['TestTaxonAPI.get_id_check'] = ['TestTaxonAPI', 'get_id']
sync_methods['TestTaxonAPI.get_id'] = True
async_run_methods['TestTaxonAPI.get_name_async'] = ['TestTaxonAPI', 'get_name']
async_check_methods['TestTaxonAPI.get_name_check'] = ['TestTaxonAPI', 'get_name']
sync_methods['TestTaxonAPI.get_name'] = True
async_run_methods['TestTaxonAPI.get_version_async'] = ['TestTaxonAPI', 'get_version']
async_check_methods['TestTaxonAPI.get_version_check'] = ['TestTaxonAPI', 'get_version']
sync_methods['TestTaxonAPI.get_version'] = True

class AsyncJobServiceClient(object):

    def __init__(self, timeout=30 * 60, token=None,
                 ignore_authrc=True, trust_all_ssl_certificates=False):
        url = environ.get('KB_JOB_SERVICE_URL', None)
        if url is None and config is not None:
            url = config.get('job-service-url')
        if url is None:
            raise ValueError('Neither \'job-service-url\' parameter is defined in '+
                    'configuration nor \'KB_JOB_SERVICE_URL\' variable is defined in system')
        scheme, _, _, _, _, _ = _urlparse.urlparse(url)
        if scheme not in ['http', 'https']:
            raise ValueError(url + " isn't a valid http url")
        self.url = url
        self.timeout = int(timeout)
        self._headers = dict()
        self.trust_all_ssl_certificates = trust_all_ssl_certificates
        if token is None:
            raise ValueError('Authentication is required for async methods')        
        self._headers['AUTHORIZATION'] = token
        if self.timeout < 1:
            raise ValueError('Timeout value must be at least 1 second')

    def _call(self, method, params, json_rpc_call_context = None):
        arg_hash = {'method': method,
                    'params': params,
                    'version': '1.1',
                    'id': str(_random.random())[2:]
                    }
        if json_rpc_call_context:
            arg_hash['context'] = json_rpc_call_context
        body = json.dumps(arg_hash, cls=JSONObjectEncoder)
        ret = _requests.post(self.url, data=body, headers=self._headers,
                             timeout=self.timeout,
                             verify=not self.trust_all_ssl_certificates)
        if ret.status_code == _requests.codes.server_error:
            if 'content-type' in ret.headers and ret.headers['content-type'] == 'application/json':
                err = json.loads(ret.text)
                if 'error' in err:
                    raise ServerError(**err['error'])
                else:
                    raise ServerError('Unknown', 0, ret.text)
            else:
                raise ServerError('Unknown', 0, ret.text)
        if ret.status_code != _requests.codes.OK:
            ret.raise_for_status()
        resp = json.loads(ret.text)
        if 'result' not in resp:
            raise ServerError('Unknown', 0, 'An unknown server error occurred')
        return resp['result']

    def run_job(self, run_job_params, json_rpc_call_context = None):
        return self._call('KBaseJobService.run_job', [run_job_params], json_rpc_call_context)[0]

    def check_job(self, job_id, json_rpc_call_context = None):
        return self._call('KBaseJobService.check_job', [job_id], json_rpc_call_context)[0]


class JSONRPCServiceCustom(JSONRPCService):

    def call(self, ctx, jsondata):
        """
        Calls jsonrpc service's method and returns its return value in a JSON
        string or None if there is none.

        Arguments:
        jsondata -- remote method call in jsonrpc format
        """
        result = self.call_py(ctx, jsondata)
        if result is not None:
            return json.dumps(result, cls=JSONObjectEncoder)

        return None

    def _call_method(self, ctx, request):
        """Calls given method with given params and returns it value."""
        method = self.method_data[request['method']]['method']
        params = request['params']
        result = None
        try:
            if isinstance(params, list):
                # Does it have enough arguments?
                if len(params) < self._man_args(method) - 1:
                    raise InvalidParamsError('not enough arguments')
                # Does it have too many arguments?
                if(not self._vargs(method) and len(params) >
                        self._max_args(method) - 1):
                    raise InvalidParamsError('too many arguments')

                result = method(ctx, *params)
            elif isinstance(params, dict):
                # Do not accept keyword arguments if the jsonrpc version is
                # not >=1.1.
                if request['jsonrpc'] < 11:
                    raise KeywordError

                result = method(ctx, **params)
            else:  # No params
                result = method(ctx)
        except JSONRPCError:
            raise
        except Exception as e:
            # log.exception('method %s threw an exception' % request['method'])
            # Exception was raised inside the method.
            newerr = ServerError()
            newerr.trace = traceback.format_exc()
            newerr.data = e.message
            raise newerr
        return result

    def call_py(self, ctx, jsondata):
        """
        Calls jsonrpc service's method and returns its return value in python
        object format or None if there is none.

        This method is same as call() except the return value is a python
        object instead of JSON string. This method is mainly only useful for
        debugging purposes.
        """
        rdata = jsondata
        # we already deserialize the json string earlier in the server code, no
        # need to do it again
#        try:
#            rdata = json.loads(jsondata)
#        except ValueError:
#            raise ParseError

        # set some default values for error handling
        request = self._get_default_vals()

        if isinstance(rdata, dict) and rdata:
            # It's a single request.
            self._fill_request(request, rdata)
            respond = self._handle_request(ctx, request)

            # Don't respond to notifications
            if respond is None:
                return None

            return respond
        elif isinstance(rdata, list) and rdata:
            # It's a batch.
            requests = []
            responds = []

            for rdata_ in rdata:
                # set some default values for error handling
                request_ = self._get_default_vals()
                self._fill_request(request_, rdata_)
                requests.append(request_)

            for request_ in requests:
                respond = self._handle_request(ctx, request_)
                # Don't respond to notifications
                if respond is not None:
                    responds.append(respond)

            if responds:
                return responds

            # Nothing to respond.
            return None
        else:
            # empty dict, list or wrong type
            raise InvalidRequestError

    def _handle_request(self, ctx, request):
        """Handles given request and returns its response."""
        if self.method_data[request['method']].has_key('types'): # @IgnorePep8
            self._validate_params_types(request['method'], request['params'])

        result = self._call_method(ctx, request)

        # Do not respond to notifications.
        if request['id'] is None:
            return None

        respond = {}
        self._fill_ver(request['jsonrpc'], respond)
        respond['result'] = result
        respond['id'] = request['id']

        return respond


class MethodContext(dict):

    def __init__(self, logger):
        self['client_ip'] = None
        self['user_id'] = None
        self['authenticated'] = None
        self['token'] = None
        self['module'] = None
        self['method'] = None
        self['call_id'] = None
        self['rpc_context'] = None
        self['provenance'] = None
        self._debug_levels = set([7, 8, 9, 'DEBUG', 'DEBUG2', 'DEBUG3'])
        self._logger = logger

    def log_err(self, message):
        self._log(log.ERR, message)

    def log_info(self, message):
        self._log(log.INFO, message)

    def log_debug(self, message, level=1):
        if level in self._debug_levels:
            pass
        else:
            level = int(level)
            if level < 1 or level > 3:
                raise ValueError("Illegal log level: " + str(level))
            level = level + 6
        self._log(level, message)

    def set_log_level(self, level):
        self._logger.set_log_level(level)

    def get_log_level(self):
        return self._logger.get_log_level()

    def clear_log_level(self):
        self._logger.clear_user_log_level()

    def _log(self, level, message):
        self._logger.log_message(level, message, self['client_ip'],
                                 self['user_id'], self['module'],
                                 self['method'], self['call_id'])


def getIPAddress(environ):
    xFF = environ.get('HTTP_X_FORWARDED_FOR')
    realIP = environ.get('HTTP_X_REAL_IP')
    trustXHeaders = config is None or \
        config.get('dont_trust_x_ip_headers') != 'true'

    if (trustXHeaders):
        if (xFF):
            return xFF.split(',')[0].strip()
        if (realIP):
            return realIP.strip()
    return environ.get('REMOTE_ADDR')


class Application(object):
    # Wrap the wsgi handler in a class definition so that we can
    # do some initialization and avoid regenerating stuff over
    # and over

    def logcallback(self):
        self.serverlog.set_log_file(self.userlog.get_log_file())

    def log(self, level, context, message):
        self.serverlog.log_message(level, message, context['client_ip'],
                                   context['user_id'], context['module'],
                                   context['method'], context['call_id'])

    def __init__(self):
        submod = get_service_name() or 'TestTaxonAPI'
        self.userlog = log.log(
            submod, ip_address=True, authuser=True, module=True, method=True,
            call_id=True, changecallback=self.logcallback,
            config=get_config_file())
        self.serverlog = log.log(
            submod, ip_address=True, authuser=True, module=True, method=True,
            call_id=True, logfile=self.userlog.get_log_file())
        self.serverlog.set_log_level(6)
        self.rpc_service = JSONRPCServiceCustom()
        self.method_authentication = dict()
        self.rpc_service.add(impl_TestTaxonAPI.get_parent,
                             name='TestTaxonAPI.get_parent',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_parent'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_children,
                             name='TestTaxonAPI.get_children',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_children'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_genome_annotations,
                             name='TestTaxonAPI.get_genome_annotations',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_genome_annotations'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_scientific_lineage,
                             name='TestTaxonAPI.get_scientific_lineage',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_scientific_lineage'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_scientific_name,
                             name='TestTaxonAPI.get_scientific_name',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_scientific_name'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_taxonomic_id,
                             name='TestTaxonAPI.get_taxonomic_id',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_taxonomic_id'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_kingdom,
                             name='TestTaxonAPI.get_kingdom',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_kingdom'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_domain,
                             name='TestTaxonAPI.get_domain',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_domain'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_genetic_code,
                             name='TestTaxonAPI.get_genetic_code',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_genetic_code'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_aliases,
                             name='TestTaxonAPI.get_aliases',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_aliases'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_info,
                             name='TestTaxonAPI.get_info',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_info'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_history,
                             name='TestTaxonAPI.get_history',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_history'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_provenance,
                             name='TestTaxonAPI.get_provenance',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_provenance'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_id,
                             name='TestTaxonAPI.get_id',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_id'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_name,
                             name='TestTaxonAPI.get_name',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_name'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.get_version,
                             name='TestTaxonAPI.get_version',
                             types=[basestring])
        self.method_authentication['TestTaxonAPI.get_version'] = 'required'
        self.rpc_service.add(impl_TestTaxonAPI.status,
                             name='TestTaxonAPI.status',
                             types=[dict])
        self.auth_client = biokbase.nexus.Client(
            config={'server': 'nexus.api.globusonline.org',
                    'verify_ssl': True,
                    'client': None,
                    'client_secret': None})

    def __call__(self, environ, start_response):
        # Context object, equivalent to the perl impl CallContext
        ctx = MethodContext(self.userlog)
        ctx['client_ip'] = getIPAddress(environ)
        status = '500 Internal Server Error'

        try:
            body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            body_size = 0
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            # we basically do nothing and just return headers
            status = '200 OK'
            rpc_result = ""
        else:
            request_body = environ['wsgi.input'].read(body_size)
            try:
                req = json.loads(request_body)
            except ValueError as ve:
                err = {'error': {'code': -32700,
                                 'name': "Parse error",
                                 'message': str(ve),
                                 }
                       }
                rpc_result = self.process_error(err, ctx, {'version': '1.1'})
            else:
                ctx['module'], ctx['method'] = req['method'].split('.')
                ctx['call_id'] = req['id']
                ctx['rpc_context'] = {'call_stack': [{'time':self.now_in_utc(), 'method': req['method']}]}
                prov_action = {'service': ctx['module'], 'method': ctx['method'], 
                               'method_params': req['params']}
                ctx['provenance'] = [prov_action]
                try:
                    token = environ.get('HTTP_AUTHORIZATION')
                    # parse out the method being requested and check if it
                    # has an authentication requirement
                    method_name = req['method']
                    if method_name in async_run_methods:
                        method_name = async_run_methods[method_name][0] + "." + async_run_methods[method_name][1]
                    if method_name in async_check_methods:
                        method_name = async_check_methods[method_name][0] + "." + async_check_methods[method_name][1]
                    auth_req = self.method_authentication.get(method_name,
                                                              "none")
                    if auth_req != "none":
                        if token is None and auth_req == 'required':
                            err = ServerError()
                            err.data = "Authentication required for " + \
                                "TestTaxonAPI but no authentication header was passed"
                            raise err
                        elif token is None and auth_req == 'optional':
                            pass
                        else:
                            try:
                                user, _, _ = \
                                    self.auth_client.validate_token(token)
                                ctx['user_id'] = user
                                ctx['authenticated'] = 1
                                ctx['token'] = token
                            except Exception, e:
                                if auth_req == 'required':
                                    err = ServerError()
                                    err.data = \
                                        "Token validation failed: %s" % e
                                    raise err
                    if (environ.get('HTTP_X_FORWARDED_FOR')):
                        self.log(log.INFO, ctx, 'X-Forwarded-For: ' +
                                 environ.get('HTTP_X_FORWARDED_FOR'))
                    method_name = req['method']
                    if method_name in async_run_methods or method_name in async_check_methods:
                        if method_name in async_run_methods:
                            orig_method_pair = async_run_methods[method_name]
                        else:
                            orig_method_pair = async_check_methods[method_name]
                        orig_method_name = orig_method_pair[0] + '.' + orig_method_pair[1]
                        if 'required' != self.method_authentication.get(orig_method_name, 'none'):
                            err = ServerError()
                            err.data = 'Async method ' + orig_method_name + ' should require ' + \
                                'authentication, but it has authentication level: ' + \
                                self.method_authentication.get(orig_method_name, 'none')
                            raise err
                        job_service_client = AsyncJobServiceClient(token = ctx['token'])
                        if method_name in async_run_methods:
                            run_job_params = {
                                'method': orig_method_name,
                                'params': req['params']}
                            if 'rpc_context' in ctx:
                                run_job_params['rpc_context'] = ctx['rpc_context']
                            job_id = job_service_client.run_job(run_job_params)
                            respond = {'version': '1.1', 'result': [job_id], 'id': req['id']}
                            rpc_result = json.dumps(respond, cls=JSONObjectEncoder)
                            status = '200 OK'
                        else:
                            job_id = req['params'][0]
                            job_state = job_service_client.check_job(job_id)
                            finished = job_state['finished']
                            if finished != 0 and 'error' in job_state and job_state['error'] is not None:
                                err = {'error': job_state['error']}
                                rpc_result = self.process_error(err, ctx, req, None)
                            else:
                                respond = {'version': '1.1', 'result': [job_state], 'id': req['id']}
                                rpc_result = json.dumps(respond, cls=JSONObjectEncoder)
                                status = '200 OK'
                    elif method_name in sync_methods or (method_name + '_async') not in async_run_methods:
                        self.log(log.INFO, ctx, 'start method')
                        rpc_result = self.rpc_service.call(ctx, req)
                        self.log(log.INFO, ctx, 'end method')
                        status = '200 OK'
                    else:
                        err = ServerError()
                        err.data = 'Method ' + method_name + ' cannot be run synchronously'
                        raise err
                except JSONRPCError as jre:
                    err = {'error': {'code': jre.code,
                                     'name': jre.message,
                                     'message': jre.data
                                     }
                           }
                    trace = jre.trace if hasattr(jre, 'trace') else None
                    rpc_result = self.process_error(err, ctx, req, trace)
                except Exception, e:
                    err = {'error': {'code': 0,
                                     'name': 'Unexpected Server Error',
                                     'message': 'An unexpected server error ' +
                                                'occurred',
                                     }
                           }
                    rpc_result = self.process_error(err, ctx, req,
                                                    traceback.format_exc())

        # print 'The request method was %s\n' % environ['REQUEST_METHOD']
        # print 'The environment dictionary is:\n%s\n' % pprint.pformat(environ) @IgnorePep8
        # print 'The request body was: %s' % request_body
        # print 'The result from the method call is:\n%s\n' % \
        #    pprint.pformat(rpc_result)

        if rpc_result:
            response_body = rpc_result
        else:
            response_body = ''

        response_headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Headers', environ.get(
                'HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'authorization')),
            ('content-type', 'application/json'),
            ('content-length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]

    def process_error(self, error, context, request, trace=None):
        if trace:
            self.log(log.ERR, context, trace.split('\n')[0:-1])
        if 'id' in request:
            error['id'] = request['id']
        if 'version' in request:
            error['version'] = request['version']
            if 'error' not in error['error'] or error['error']['error'] is None:
                error['error']['error'] = trace
        elif 'jsonrpc' in request:
            error['jsonrpc'] = request['jsonrpc']
            error['error']['data'] = trace
        else:
            error['version'] = '1.0'
            error['error']['error'] = trace
        return json.dumps(error)

    def now_in_utc(self):
        # Taken from http://stackoverflow.com/questions/3401428/how-to-get-an-isoformat-datetime-string-including-the-default-timezone
        dtnow = datetime.datetime.now()
        dtutcnow = datetime.datetime.utcnow()
        delta = dtnow - dtutcnow
        hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
        return "%s%+02d:%02d" % (dtnow.isoformat(), hh, mm)

application = Application()

# This is the uwsgi application dictionary. On startup uwsgi will look
# for this dict and pull its configuration from here.
# This simply lists where to "mount" the application in the URL path
#
# This uwsgi module "magically" appears when running the app within
# uwsgi and is not available otherwise, so wrap an exception handler
# around it
#
# To run this server in uwsgi with 4 workers listening on port 9999 use:
# uwsgi -M -p 4 --http :9999 --wsgi-file _this_file_
# To run a using the single threaded python BaseHTTP service
# listening on port 9999 by default execute this file
#
try:
    import uwsgi
# Before we do anything with the application, see if the
# configs specify patching all std routines to be asynch
# *ONLY* use this if you are going to wrap the service in
# a wsgi container that has enabled gevent, such as
# uwsgi with the --gevent option
    if config is not None and config.get('gevent_monkeypatch_all', False):
        print "Monkeypatching std libraries for async"
        from gevent import monkey
        monkey.patch_all()
    uwsgi.applications = {
        '': application
        }
except ImportError:
    # Not available outside of wsgi, ignore
    pass

_proc = None


def start_server(host='localhost', port=0, newprocess=False):
    '''
    By default, will start the server on localhost on a system assigned port
    in the main thread. Excecution of the main thread will stay in the server
    main loop until interrupted. To run the server in a separate process, and
    thus allow the stop_server method to be called, set newprocess = True. This
    will also allow returning of the port number.'''

    global _proc
    if _proc:
        raise RuntimeError('server is already running')
    httpd = make_server(host, port, application)
    port = httpd.server_address[1]
    print "Listening on port %s" % port
    if newprocess:
        _proc = Process(target=httpd.serve_forever)
        _proc.daemon = True
        _proc.start()
    else:
        httpd.serve_forever()
    return port


def stop_server():
    global _proc
    _proc.terminate()
    _proc = None

def process_async_cli(input_file_path, output_file_path, token):
    exit_code = 0
    with open(input_file_path) as data_file:    
        req = json.load(data_file)
    if 'version' not in req:
        req['version'] = '1.1'
    if 'id' not in req: 
        req['id'] = str(_random.random())[2:]
    ctx = MethodContext(application.userlog)
    if token:
        user, _, _ = application.auth_client.validate_token(token)
        ctx['user_id'] = user
        ctx['authenticated'] = 1
        ctx['token'] = token
    if 'context' in req:
        ctx['rpc_context'] = req['context']
    ctx['CLI'] = 1
    ctx['module'], ctx['method'] = req['method'].split('.')
    prov_action = {'service': ctx['module'], 'method': ctx['method'], 
                   'method_params': req['params']}
    ctx['provenance'] = [prov_action]
    resp = None
    try:
        resp = application.rpc_service.call_py(ctx, req)
    except JSONRPCError as jre:
        trace = jre.trace if hasattr(jre, 'trace') else None
        resp = {'id': req['id'],
                'version': req['version'],
                'error': {'code': jre.code,
                          'name': jre.message,
                          'message': jre.data,
                          'error': trace}
               }
    except Exception, e:
        trace = traceback.format_exc()
        resp = {'id': req['id'],
                'version': req['version'],
                'error': {'code': 0,
                          'name': 'Unexpected Server Error',
                          'message': 'An unexpected server error occurred',
                          'error': trace}
               }
    if 'error' in resp:
        exit_code = 500
    with open(output_file_path, "w") as f:
        f.write(json.dumps(resp, cls=JSONObjectEncoder))
    return exit_code
    
if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    if len(sys.argv) >= 3 and len(sys.argv) <= 4 and os.path.isfile(sys.argv[1]):
        token = None
        if len(sys.argv) == 4:
            if os.path.isfile(sys.argv[3]):
                with open(sys.argv[3]) as token_file: 
                    token = token_file.read()
            else:
                token = sys.argv[3]
        sys.exit(process_async_cli(sys.argv[1], sys.argv[2], token))
    try:
        opts, args = getopt(sys.argv[1:], "", ["port=", "host="])
    except GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        sys.exit(2)
    port = 9999
    host = 'localhost'
    for o, a in opts:
        if o == '--port':
            port = int(a)
        elif o == '--host':
            host = a
            print "Host set to %s" % host
        else:
            assert False, "unhandled option"

    start_server(host=host, port=port)
#    print "Listening on port %s" % port
#    httpd = make_server( host, port, application)
#
#    httpd.serve_forever()
