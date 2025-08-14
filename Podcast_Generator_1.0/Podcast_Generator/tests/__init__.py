import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#Fichiers Tests
dossier = "Samples"
nom_fichier = "test.txt"

def run_tests():

    #Load all tests #Estimate  640.317s/10min
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=".", pattern="test_*.py")
    runner = unittest.TextTestRunner()

    #Runs all tests
    test_results = runner.run(suite)
    return test_results.wasSuccessful()

if __name__ == "__main__":
    test_results = run_tests()
    if not test_results:
        exit(-1)