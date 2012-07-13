#! /usr/bin/env python

import os, re, signal, sys, time, hashlib
import boinc_path_config
from Boinc import database, boinc_db, boinc_project_path, configxml, sched_messages
from xml.dom.minidom import parseString
import magphys_assimilator

class DummyWorkUnit:
    id = 1
    canonical_result = None
    xml_doc_in = ""
    
class DummyResult:
    user = None
    
class DummyConfig:
    upload_dir = ""
    uldl_dir_fanout = 1

class MagphysAssimilatorTest(magphys_assimilator.MagphysAssimilator):
    
    def __init__(self):
        magphys_assimilator.MagphysAssimilator.__init__(self)
    
    def test(self, uploadDir, outFile):
        str_list = []
        str_list.append("<file_info>\n")
        str_list.append("    <name>")
        str_list.append(outFile)
        str_list.append("    </name>\n")
        str_list.append("    <generated_locally/>\n")
        str_list.append("    <upload_when_present/>\n")
        str_list.append("    <max_nbytes>1000000</max_nbytes>\n")
        str_list.append("    <url>\n")
        str_list.append("        http://ec2-23-21-160-71.compute-1.amazonaws.com/pogs_cgi/file_upload_handler\n")
        str_list.append("    </url>\n")
        str_list.append("</file_info>\n")
        str_list.append("<result>\n")
        str_list.append("    <file_ref>\n")
        str_list.append("        <file_name>")
        str_list.append(outFile)
        str_list.append("</file_name>\n")
        str_list.append("        <open_name>output.fit</open_name>\n")
        str_list.append("        <copy_file/>\n")
        str_list.append("    </file_ref>\n")
        str_list.append("</result>\n")
        #str_list.append("<?xml version=\"1.0\" ?>\n")
        #str_list.append("<output>\n")
        #str_list.append("  <file_name>")
        #str_list.append(outFile)
        #str_list.append("</file_name>\n")
        #str_list.append("</output>")
        #print ''.join(str_list)
        
        self.config = DummyConfig()
        self.config.upload_dir = uploadDir
        self.config.uldl_dir_fanout = 1024
        
        result1 = DummyResult()
        result1.userid = 1
        result2 = DummyResult()
        result2.userid = 2
        results = [result1,result2]
        
        canonical_result = DummyResult()
        canonical_result.xml_doc_in = ''.join(str_list)
        
        wu = DummyWorkUnit()
        wu.canonical_result = result1
        self.assimilate_handler(wu, results, canonical_result)
        
        #session = self.Session()
        #self.processResult(session, sedFile, fitFile, results)
        #session.commit()
    
if __name__ == '__main__':
    asm = MagphysAssimilatorTest()
    asm.test("/Users/rob", "magphys/output.fit")