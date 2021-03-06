################################################################################
#
# Library: pydstk
#
# Copyright 2010 Kitware Inc. 28 Corporate Drive,
# Clifton Park, NY, 12065, USA.
#
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 ( the "License" );
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################


"""Testing for dscore/system.py
"""


import os
import sys
import json
import copy
import pickle
import unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dscore.system import LinearDS
from dsutil.dsutil import loadDataFromASCIIFile, orth
from dscore.system import NonLinearDS
from dscore.dskpca import KPCAParam, rbfK, RBFParam


TESTBASE = os.path.dirname(__file__) 


def test_LinearDS_check():
    """Test LinearDS parameter checking.
    """
    
    lds = LinearDS(5, False, False)
    assert lds.check() is False


def test_NonLinearDS_check():
    """Test NonLinearDS parameter checking.
    """
    
    kpcaP = KPCAParam()
    kpcaP._kPar = RBFParam()
    kpcaP._kPar._kCen = True
    kpcaP._kFun = rbfK
    
    nlds = NonLinearDS(5, kpcaP, False)
    assert nlds.check() is False


def test_LinearDS_suboptimalSysID(): 
    """Test LinearDS system identification.
    """
    
    dataFile = os.path.join(TESTBASE, "data/data1.txt")
    data, _ = loadDataFromASCIIFile(dataFile)
     
    lds = LinearDS(5, False, False)
    lds.suboptimalSysID(data)
     
    baseLDSFile = os.path.join(TESTBASE, "data/data1-dt-5c-center.pkl")
    baseLDS = pickle.load(open(baseLDSFile))
     
    _, err = LinearDS.stateSpaceMap(baseLDS, lds)
    assert np.allclose(err, 0.0) == True


def test_NonLinearDS_suboptimalSysID(): 
    """Test NonLinearDS system identification.
    """

    dataFile = os.path.join(TESTBASE, "data/data1.txt")
    data, _ = loadDataFromASCIIFile(dataFile)
    
    kpcaP = KPCAParam()
    kpcaP._kPar = RBFParam()
    kpcaP._kPar._kCen = True
    kpcaP._kFun = rbfK
         
    nlds = NonLinearDS(5, kpcaP, False)
    nlds.suboptimalSysID(data)

    baseNLDSFile = os.path.join(TESTBASE, "data/data1-rbf-kdt-5c-center.pkl")
    baseNLDS = pickle.load(open(baseNLDSFile))
    
    err = NonLinearDS.naiveCompare(baseNLDS, nlds)
    assert np.allclose(err, 0.0) == True
    
    
def test_computeRJF_part0():
    """Test computeRJF() with random 3x3 ... 10x10 matrices.
    """
    
    np.random.seed(1234)
    for d in range(3,10):
        A = np.random.random((d,d))
        J,T,_ = LinearDS.computeRJF(A)
        Ac = T.dot(A).dot(np.linalg.inv(T))
        np.testing.assert_almost_equal(np.linalg.norm(J-Ac, 'fro'), 0)


def test_computeRJF_part1():
    """Test computeRJF() with MATLAB example.
    """ 
    
    # MATLAB test example, see 'doc jordan' in MATLAB
    A = np.asarray([[1,-3,-2],
                    [-1,1,-1],
                    [2,4,5]])
    J,T,_ = LinearDS.computeRJF(A)
    ref = np.asarray([[3,0,0],
                      [0,2,0],
                      [0,0,2]])
    np.testing.assert_almost_equal(np.linalg.norm(J-ref,'fro'), 0)


def test_convertToJCF():
    """Test JCF w.r.t. similarity transforms (random orth. matrices)
    """
    
    np.random.seed(1234)
    dsFile = os.path.join(TESTBASE, "data/data1-dt-5c-center.pkl")
    ds = pickle.load(open(dsFile))
    
    # extract real (A,C) pair
    A,C,N = ds._Ahat, ds._Chat, ds._nStates
    P = LinearDS.computeJCFTransform(A,C)
    
    # compute JCF of original LDS's (A,C) pair
    Ac = P*A*np.linalg.inv(P) 
    Cc = C*np.linalg.inv(P)

    # create random orthogonal matrices
    for i in range(100):
        Q = orth(np.random.random((N,N)))
        
        # apply similarity transform on (A,C)
        tC = C.dot(np.linalg.inv(Q))
        tA = Q*A*np.linalg.inv(Q)

        # now, compute the JCF transform and apply it
        R = LinearDS.computeJCFTransform(tA,tC)
        Ar = R*tA*np.linalg.inv(R)
        Cr = tC*np.linalg.inv(R) 
        
        # ensure that (A,C)'s remain equal
        errA = np.linalg.norm(Ac-Ar, 'fro') 
        errC = np.linalg.norm(Cc-Cr, 'fro') 
        np.testing.assert_almost_equal(errA, 0, 5)
        np.testing.assert_almost_equal(errC, 0, 5)
    
    
if __name__ == "__main__":
    pass
    








    
    
    
    