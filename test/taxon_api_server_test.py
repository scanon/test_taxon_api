import unittest
import os
import json
import time

from os import environ
from ConfigParser import ConfigParser
from pprint import pprint

from biokbase.workspace.client import Workspace as workspaceService
from test_taxon_api.test_taxon_apiImpl import test_taxon_api
from test_taxon_api.test_taxon_apiServer import MethodContext


class test_taxon_apiTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'provenance': [
                            {'service': 'taxon_api',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('test_taxon_api'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = test_taxon_api(cls.cfg)
        cls.taxon='1779/523209/1'
        cls.parent=u'1779/178590/1'

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_taxon_api_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_your_method(self):
        # Prepare test objects in workspace if needed using 
        # self.getWsClient().save_objects({'workspace': self.getWsName(), 'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        pass

    def test_get_parent(self):
        ret = self.getImpl().get_parent(self.getContext(), self.taxon)
        self.assertEqual(ret[0],self.parent)

    def test_get_children(self):
        ret = self.getImpl().get_children(self.getContext(), self.taxon)
        self.assertEqual(ret[0],[])

    def test_get_genome_annotations(self):
        ret = self.getImpl().get_genome_annotations(self.getContext(), self.taxon)
        self.assertEqual(ret[0],['5810/70/1','6838/147/2','6831/12/1','5729/70/1','1837/570/3','1374/676/1','5441/70/1','4758/9/1','4435/71/2','4237/79/1'] )

    def test_get_scientific_lineage(self):
        ret = self.getImpl().get_scientific_lineage(self.getContext(), self.taxon)
        self.assertEqual(ret[0], [u'cellular organisms', u'Eukaryota', u'Rhodophyta', u'Bangiophyceae', u'Cyanidiales', u'Cyanidiaceae', u'Cyanidioschyzon', u'Cyanidioschyzon merolae'])

    def test_get_scientific_name(self):
        ret = self.getImpl().get_scientific_name(self.getContext(), self.taxon)
        self.assertEqual(ret[0],u'Cyanidioschyzon merolae strain 10D')

    def test_get_taxonomic_id(self):
        ret = self.getImpl().get_taxonomic_id(self.getContext(), self.taxon)
        self.assertEqual(ret[0],280699)

    #def test_get_kingdom(self):
    #    ret = self.getImpl().get_kingdom(self.getContext(), self.taxon)
    #    print ret
    #    self.assertEqual(ret[0],u'cellular organisms')

    def test_get_domain(self):
        ret = self.getImpl().get_domain(self.getContext(), self.taxon)
        self.assertEqual(ret[0], u'Eukaryota')

    def test_get_genetic_code(self):
        ret = self.getImpl().get_genetic_code(self.getContext(), self.taxon)
        self.assertEqual(ret[0],1)

    def test_get_aliases(self):
        ret = self.getImpl().get_aliases(self.getContext(), self.taxon)
        print ret
        self.assertEqual(ret[0],[])

    def test_get_info(self):
        ret = self.getImpl().get_info(self.getContext(), self.taxon)
        print ret
        self.assertEqual(ret[0], {'type_string': u'KBaseGenomeAnnotations.Taxon-1.0', 'workspace_id': 1779, 'object_checksum': u'5f1b24082f447daccca0c8d2f1073fe4', 'object_reference': '1779/523209', 'object_size': 455, 'saved_by': u'kbasetest', 'object_id': 523209, 'save_date': u'2015-10-08T18:44:34+0000', 'object_metadata': None, 'object_name': u'280699_taxon', 'version': 1, 'workspace_name': u'ReferenceTaxons', 'object_reference_versioned': '1779/523209/1'} )

    def test_get_history(self):
        ret = self.getImpl().get_history(self.getContext(), self.taxon)
        print ret
        self.assertEqual(ret[0], [{'object_checksum': u'5f1b24082f447daccca0c8d2f1073fe4', 'object_id': 523209, 'object_metadata': {}, 'object_name': u'280699_taxon', 'object_reference': '1779/523209', 'object_reference_versioned': '1779/523209/1', 'object_size': 455, 'save_date': u'2015-10-08T18:44:34+0000', 'saved_by': u'kbasetest', 'type_string': u'KBaseGenomeAnnotations.Taxon-1.0', 'version': 1, 'workspace_id': 1779, 'workspace_name': u'ReferenceTaxons'}])

    def test_get_provenance(self):
        ret = self.getImpl().get_provenance(self.getContext(), self.taxon)
        print ret
        self.assertEqual(ret[0], [{'description': u'taxon generated from NCBI taxonomy names and nodes files downloaded on 7/20/2015.', 'script_name': u'make_taxons.py', 'script_version': u'0.1'}])

    def test_get_id(self):
        ret = self.getImpl().get_id(self.getContext(), self.taxon)
        print ret
        self.assertEqual(ret[0],523209)

    def test_get_name(self):
        ret = self.getImpl().get_name(self.getContext(), self.taxon)
        self.assertEqual(ret[0], u'280699_taxon')

    def test_get_version(self):
        ret = self.getImpl().get_version(self.getContext(), self.taxon)
        self.assertEqual(ret[0],'1')

