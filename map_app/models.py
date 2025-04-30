# Alyssa, Payton

from django.db import models

# Bird Species Model
class Species(models.Model):
    speciesID = models.IntegerField(unique = True)
    species = models.CharField(max_length=200)
    birdcode = models.CharField(max_length=10)

    #ordering of birds
    class Meta:
        ordering = ['species']

#Grid Model
class Grid(models.Model):
    OID = models.IntegerField(unique = True)
    Grid_ID	= models.CharField(max_length=50, unique = True)
    Grid_E_NAD83 = models.IntegerField()
    Grid_N_NAD83 = models.IntegerField()
    UTM_Zone = models.IntegerField()
    Grid_Lat_NAD83 = models.FloatField()
    Grid_Long_NAD83	= models.FloatField()
    BCR	= models.IntegerField()
    MgmtEntity = models.CharField(max_length=200)
    MgmtRegion = models.CharField(max_length=200)
    MgmtUnit = models.CharField(max_length=200)
    MgmtDistrict = models.CharField(max_length=200)
    County = models.CharField(max_length=200)
    State = models.CharField(max_length=5)
    PriorityLandscape = models.CharField(max_length=200)
    inPL = models.BooleanField()

#Results Model
class Results(models.Model):
    bird_speciesID = models.ForeignKey(Species, on_delete=models.CASCADE)
    gridID = models.ForeignKey(Grid, on_delete=models.CASCADE)
    lbci = models.FloatField()
    posterior_median = models.FloatField()
    ubci = models.FloatField()
    