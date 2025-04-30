#Everyone

from django.test import TestCase
from django.core.management import call_command
from .models import Species, Grid, Results
import csv
from io import StringIO
import os
        
# tests for adding data
class AddingDataTests(TestCase):
    def setUp(self):
        Species.objects.create(speciesID=0, species="Fake Bird", birdcode="BIRDCODE")
        
        Grid.objects.create(OID=1, Grid_ID="NM-CARSON-LE1", Grid_E_NAD83=388500,Grid_N_NAD83=4091500,UTM_Zone=13,Grid_Lat_NAD83=36.96299337,Grid_Long_NAD83=-106.2525113,BCR=16,MgmtEntity="US Forest Service", MgmtRegion="USFS Region 3",MgmtUnit="Carson National Forest",MgmtDistrict="Tres Piedras Ranger District",County="Rio Arriba",State="NM",PriorityLandscape="Enchanted Circle",inPL=0)

        Results.objects.create(bird_speciesID=0, gridID= 0, lbci= 1.1, posterior_median= 2.2, ubci=3.3)
    
    
    def test_adding_bird_and_result_only(self):
        """
        checks that the bird and result were added correctly to the database.
        """

# csv to db tests
class csvTests(TestCase):
    
    # create error-triggering files
    def setUp(self):
        # save test file names
        self.fileNames = ["badFileHeader.csv", "incompleteFileHeader.csv", "badFileContentSpecies.csv", "badFileContentGrid.csv",
                      "badFileContentResults.csv", "badFileType.py"]
        
        # create a file w/o any of the right headers
        with open("badFileHeader.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["this is", "NOT a valid", "csv"])
            writer.writerow(["1", "American Crow", "AMCR"])

        # create a file w/ just an acceptable first field
        with open("incompleteFileHeader.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["ï»¿OID_"])
            writer.writerow(["1", "American Crow", "AMCR"])
        
        # create a Species file with bad data
        with open("badFileContentSpecies.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["speciesID","species","birdcode"])
            writer.writerow(["this can't be an int!"])

        # create a Grid file with bad data
        with open("badFileContentGrid.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["ï»¿OID_","Grid_ID","Grid_E_NAD83","Grid_N_NAD83","UTM_Zone","Grid_Lat_NAD83","Grid_Long_NAD83","BCR",
                              "MgmtEntity","MgmtRegion","MgmtUnit","MgmtDistrict","County","State","PriorityLandscape","inPL"])
            writer.writerow(["this can't be an int!"])
        
        # create a Results file with bad data
        with open("badFileContentResults.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["parameter","lbci","posterior.median","ubci"])
            writer.writerow(["this can't be an int!"])

        # create a non-csv file
        with open("badFileType.py", "w") as file:
            file.write("var = 10")

    # test the file with an incorrect field name
    def test_bad_file_header(self):
        errText = StringIO()
        call_command("populate", "badFileHeader.csv", stderr=errText)
        self.assertIn("Error: Invalid first field. File must be Species, Grid, or Results", errText.getvalue())

    # test the file with an incomplete field name
    def test_incomplete_field_header(self):
        errText = StringIO()
        call_command("populate", "incompleteFileHeader.csv", stderr=errText)
        self.assertIn("Error: Invalid first field. File must be Species, Grid, or Results", errText.getvalue())

    # test the Species file with bad data
    def test_bad_file_content_species(self):
        errText = StringIO()
        call_command("populate", "badFileContentSpecies.csv", stderr=errText)
        self.assertIn("Error: Incorrect file value", errText.getvalue())

    # test the Grid file with bad data
    def test_bad_file_content_grid(self):
        errText = StringIO()
        call_command("populate", "badFileContentGrid.csv", stderr=errText)
        self.assertIn("Error: Incorrect file value", errText.getvalue())
    
    # test the Results file with bad data
    def test_bad_file_content_results(self):
        errText = StringIO()
        call_command("populate", "badFileContentResults.csv", stderr=errText)
        self.assertIn("Error: Incorrect file value", errText.getvalue())

    # test the incorrect file type
    def test_bad_file_type(self):
        errText = StringIO()
        call_command("populate", "badFileType.py", stderr=errText)
        self.assertIn("Error: Wrong file type. Must be csv", errText.getvalue())

    # test inputting a non-file
    def test_invalid_file_type(self):
        errText = StringIO()
        call_command("populate", "abcdefghijklmnopqrstuvwxyz", stderr=errText)
        self.assertIn("Error: File inaccessible", errText.getvalue())

    # tear down function
    def tearDown(self):
        # for every file in the list of test files
        for file in self.fileNames:
            # if it exists
            if os.path.exists(file):
                # delete it
                os.remove(file)