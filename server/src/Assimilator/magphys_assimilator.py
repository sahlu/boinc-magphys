
import Assimilator
import os, re, signal, sys, time, hashlib
import boinc_path_config
from Boinc import database, boinc_db, boinc_project_path, configxml, sched_messages
from xml.dom.minidom import parseString

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class WorkUnit(Base):
    __tablename__ = 'work_unit'
    
    work_unit_id = Column(Integer, primary_key=True)
    point_name = Column(String(100))
    i_sfh = Column(Float)
    i_ir = Column(Float)
    chi2 = Column(Float)
    redshift = Column(Float)
    a = Column(Float)
    fmu_sfh = Column(Float)
    fmu_ir = Column(Float)
    mu = Column(Float)
    tauv = Column(Float)
    s_sfr = Column(Float)
    m = Column(Float)
    ldust = Column(Float)
    t_w_bc = Column(Float)
    t_c_ism = Column(Float)
    xi_c_tot = Column(Float)
    xi_pah_tot = Column(Float)
    xi_mir_tot = Column(Float)
    x_w_tot = Column(Float)
    tvism = Column(Float)
    mdust = Column(Float)
    sfr = Column(Float)
    #filters = relationship("WorkUnitFilter", order_by="WorkUnitFilter.filter_name", backref="work_unit")
    
class WorkUnitFilter(Base):
    __tablename__ = 'work_unit_filter'
    
    filter_id = Column(Integer, primary_key=True)
    work_unit_id = Column(Integer, ForeignKey('work_unit.work_unit_id'))
    filter_name = Column(String(100))
    observed_flux = Column(Float)
    observational_uncertainty = Column(Float)
    flux_bfm = Column(Float)
    
    work_unit = relationship("WorkUnit", backref=backref('filters', order_by=filter_id))
    
class WorkUnitParameter(Base):
    __tablename__ = 'work_unit_parameter'
    
    parameter_id = Column(Integer, primary_key=True)
    work_unit_id = Column(Integer, ForeignKey('work_unit.work_unit_id'))
    parameter_name = Column(String(100))
    percentile2_5 = Column(Float)
    percentile16 = Column(Float)
    percentile50 = Column(Float)
    percentile84 = Column(Float)
    percentile97_5 = Column(Float)
    
    work_unit = relationship("WorkUnit", backref=backref('parameters', order_by=parameter_id))

class WorkUnitHistogram(Base):
    __tablename__ = 'work_unit_histogram'
    
    histogram_id = Column(Integer, primary_key=True)
    parameter_id = Column(Integer, ForeignKey('work_unit_parameter.parameter_id'))
    x_axis = Column(Float)
    hist_value = Column(Float)
    
    parameter = relationship("WorkUnitParameter", backref=backref('histograms', order_by=histogram_id))
            
class MagphysAssimilator(Assimilator.Assimilator):
    
    def __init__(self):
        Assimilator.Assimilator.__init__(self)
        #super(MagphysAssimilator, self).__init__(self)
        
        engine = create_engine("mysql://root:@localhost/magphys_as")
        self.Session = sessionmaker(bind=engine)
        #Session = sessionmaker()
        #Session.configure(bind=engine)
    
    def get_output_file_infos(self, result, list):
        dom = parseString(result.xml_doc_in)
        for node in dom.getElementsByTagName('file_ref'):
            print node
            list.append(node.nodeValue)
            #list.append(node.data)
        return dom.getElementsByTagName('file_ref')
    
    def processFiles(self, sedFile, fitFile):
        parts = fitFile.split('/')
        last = parts[len(parts)-1]
        parts = last.split('.')
        pointName = parts[0]
        print 'Point Name',
        print pointName
        #f = open(sedFile , "r")
        #for line in f:
        #    print line,
        #f.close()
        
        session = self.Session()
        wu = session.query(WorkUnit).filter("point_name=:name").params(name=pointName).first()
        doAdd = False
        if (wu == None):
            wu = WorkUnit()
        else:
            for filter in wu.filters:
                session.delete(filter)
            for parameter in wu.parameters:
                for histogram in parameter.histograms:
                    session.delete(histogram)
                session.delete(parameter)
        wu.point_name = pointName;
        wu.filters = []
        wu.parameters = []
        
        self.processFitFile(fitFile, pointName, wu)
        
        if wu.work_unit_id == None:
            session.add(wu)
        session.commit()
    
    def processFitFile(self, fitFile, pointName, wu):
        f = open(fitFile , "r")
        lineNo = 0
        #parameterName = None
        parameter = None
        percentilesNext = False
        histogramNext = False
        for line in f:
            lineNo = lineNo + 1
            
            if lineNo == 2:
                filterNames = line.split()
                for filterName in filterNames:
                    if filterName != '#':
                        filter = WorkUnitFilter()
                        filter.filter_name = filterName
                        wu.filters.append(filter)
            elif lineNo == 3:
                idx = 0
                values = line.split()
                for value in values:
                    filter = wu.filters[idx]
                    filter.observed_flux = float(value)
                    idx = idx + 1
            elif lineNo == 4:
                idx = 0
                values = line.split()
                for value in values:
                    filter = wu.filters[idx]
                    filter.observational_uncertainty = float(value)
                    idx = idx + 1
            elif lineNo == 9:
                values = line.split()
                wu.i_sfh = float(values[0])
                wu.i_ir = float(values[1])
                wu.chi2 = float(values[2])
                wu.redshift = float(values[3])
                #for value in values:
                #    print value
            elif lineNo == 11:
                values = line.split()
                wu.fmu_sfh = float(values[0])
                wu.fmu_ir = float(values[1])
                wu.mu = float(values[2])
                wu.tauv = float(values[3])
                wu.s_sfr = float(values[4])
                wu.m = float(values[5])
                wu.ldust = float(values[6])
                wu.t_w_bc = float(values[7])
                wu.t_c_ism = float(values[8])
                wu.xi_c_tot = float(values[9])
                wu.xi_pah_tot = float(values[10])
                wu.xi_mir_tot = float(values[11])
                wu.x_w_tot = float(values[12])
                wu.tvism = float(values[13])
                wu.mdust = float(values[14])
                wu.sfr = float(values[15])
            elif lineNo == 13:
                idx = 0
                values = line.split()
                for value in values:
                    filter = wu.filters[idx]
                    filter.flux_bfm = float(value)
                    idx = idx + 1
            elif lineNo > 13:
                if line.startswith("# ..."):
                    parts = line.split('...')
                    parameterName = parts[1].strip()
                    #print "parameterName is",
                    #print parameterName
                    parameter = WorkUnitParameter()
                    parameter.parameter_name = parameterName;
                    wu.parameters.append(parameter)
                    percentilesNext = False;
                    histogramNext = True
                elif line.startswith("#....percentiles of the PDF......") and parameter != None:
                    percentilesNext = True;
                    histogramNext = False
                elif percentilesNext:
                    values = line.split()
                    parameter.percentile2_5 = float(values[0])
                    parameter.percentile16 = float(values[1])
                    parameter.percentile50 = float(values[2])
                    parameter.percentile84 = float(values[3])
                    parameter.percentile97_5 = float(values[4])
                    percentilesNext = False;
                elif histogramNext:
                    hist = WorkUnitHistogram()
                    values = line.split()
                    hist.x_axis = float(values[0])
                    hist.hist_value = float(values[1])
                    parameter.histograms.append(hist)
                    
        f.close()
        
    def assimilate_handler(self, wu, results, canonical_result):
        
        print "Testing"
        #engine = create_engine("mysql://root:@localhost/magphys_as")
        #Base = declarative_base()
        #Session = sessionmaker(bind=engine)
        #Session = sessionmaker()
        #Session.configure(bind=engine)
        session = Session()
        #ed_user = User('ed', 'Ed Jones', 'edspassword')
        #session.add(ed_user)
        #our_user = session.query(User).filter_by(name='ed').first()
        #wu = session.query(WorkUnit).filter("point_name=:name").params(name="abc").first()
        wu = WorkUnit()
        session.commit()
        
        #db=_mysql.connect("localhost", "root", "", "magphys-boinc")
        
        #c=db.cursor()
        #max_price=5
        #c.execute("""SELECT spam, eggs, sausage FROM breakfast
        #  WHERE price < %s""", (max_price,))

        if (wu.canonical_resultid):
            file_list = []
            self.get_output_file_infos(canonical_result, file_list)
            
            sedFile = None;
            fitFile = None;
            for file in file_list:
                processFile(file)
                if (fileName.endswith(".sed")):
                    sedFile = fileName
                elif (fileName.endswith(".fit")):
                    fitFile = fileName
                    
            if (sedFile and fitFile):
                pass
            else:
                self.logCritical("Both of the sed and fit files were not returned\n")
        else:
            reportErrors(su)
            
        return 0;

    def processFit(self, fitFile):
        print fitFile

    
if __name__ == '__main__':
    asm = MagphysAssimilator()
    asm.run()