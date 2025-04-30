#Everyone

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, FileResponse
from csp.decorators import csp_exempt
import csv, datetime, time
from django.core.management import call_command
import subprocess, sys

from .models import Species, Grid, Results

def index(request):
    # set page to load
    index_page = "home.html"
    
    # defines what happens when there is a GET request
    if request.method == "GET":
        return render(request, index_page)


@csp_exempt  # currently not enforcing the set csp protection rules
def map(request):
    # set page to load
    map_page = "map.html"
    # gets all the birds
    birds = Species.objects.all()
    

    if request.method == "GET":
            # Check if an update was recently applied.
            if not request.session.get("filter_applied", False):
                # Initial load: generate the full DB heatmap.
                run_django_command("create_heatmap_all")
                run_django_command("generate_enchanted_circle_map_all")
            else:
                # Clear the flag so future GETs will run the full DB commands again.
                request.session["filter_applied"] = False

            timestamp = datetime.datetime.now().timestamp()
            return render(request, map_page, {'birds': birds, 'timestamp': timestamp, 'embed': True})
        
    if request.method == "POST":
        # Get the list of bird species requested.
        birdList = request.POST.getlist("birdSpecies")
        # Create new CSV file with current parameters.
        getCSV(birdList)
        # Update map with filtered commands.
        run_django_command("create_heatmap")
        run_django_command("generate_enchanted_circle_map")
        # Set a flag so that the GET branch does not override the filtered map.
        request.session["filter_applied"] = True
        time.sleep(10)
        # Redirect to force a fresh GET request.
        return redirect('/map/')


#add search method



def run_django_command(command):
    try:
        subprocess.run(
            [sys.executable, 'manage.py'] + command.split(),
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed: {e.stderr}")


@csp_exempt  # currently not enforcing the set csp protection rules
def download(request):
    
    # get date and time for export name
    curTime = datetime.datetime.now()
    timeStr = curTime.strftime("%m-%d-%Y_%H_%M")

    #create file download
    response = FileResponse(open("bird_data.csv", 'rb'))
    response['Content-Type'] = "text/csv"
    response['Content-Disposition'] = f'attachment; filename="bird_data_{timeStr}.csv"'

    return response


@csp_exempt  # currently not enforcing the set csp protection rules
def enchanted_circle_map(request):
    # get the embed variable
    embed = request.GET.get('embed')

    # add to a dictionary to pass into the render template
    context = {
        'embed': embed
    }

    # render the template, with embed variable
    response = render(request, 'enchanted_circle_map.html', context)

    # Force the browser not to cache this response
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@csp_exempt
def query(request, modelName):
    # Create the HttpResponse object with the appropriate CSV header.
    filename = f"{modelName.lower()}_data.csv"
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

    # make sure a valid model type is being requested
    modelDict = {
        "Species": Species,
        "species": Species,
        "Grid": Grid,
        "grid": Grid,
        "Results": Results,
        "results": Results
    }

    # get the db model/table we want:
    modelChoice = modelDict.get(modelName)
    # otherwise, return an error
    if modelChoice is None:
        return HttpResponseNotFound("<h1>Error: Model Not Found!</h1>")
    
    # start a csv writer
    writer = csv.writer(response)

    # get the fields and write them to the csv
    fields = [field.name for field in modelChoice._meta.fields]
    writer.writerow(fields)

    # get all elements of model from db
    modelQuerySet = modelChoice.objects.all()

    # write all elements to the csv
    for entry in modelQuerySet:
        # variable for holding current row
        row = []

        # for field in database row's fields
        for field in fields:
            # get the attribute's value
            value = getattr(entry, field)

            # find out what it is
            fieldObj = modelChoice._meta.get_field(field)
            
            # if a primary key, get the key's id value
            if fieldObj.is_relation:
                value = getattr(value, "id", value)

            # add value to the current row
            row.append(value)

        # write the current row to the csv
        writer.writerow(row)

    # return the http response, download the csv
    return response


@csp_exempt
def instructions(request):
    instructions_page = "instructions.html"

    # defines what happens when there is a GET request
    if request.method == "GET":
        return render(request, instructions_page)
    

#####################################################
#             Query to csv functions                #
#####################################################

# takes in list of bird species ids, creates and returns CSV file with specified results
def getCSV(birdList):
    # Create the csv file name
    filename = "bird_data.csv"

    # creates and opens new csv file
    with open(filename, 'w', newline='') as csvOutput:
        # start a csv writer
        writer = csv.writer(csvOutput)

        # get relevant rows
        outputResults = Results.objects.filter(bird_speciesID__speciesID__in=birdList)

        # get the fields and write them to the csv
        fields = ["grid_OID", "species", "birdcode", "lbci", "posterior_median", "ubci"]
        writer.writerow(fields)

        # print all the lines in the results table to the csv
        for entry in outputResults:
            # variable for holding current row
            row = []

            # get grid OID
            gridID = getattr(entry.gridID, "id")
            gridObject = Grid.objects.get(id=gridID)
            # add grid_OID to the current row
            row.append(gridObject.OID)    
            
            # get species name and birdcode
            speciesID = getattr(entry.bird_speciesID, "id")
            speciesObject = Species.objects.get(id=speciesID)
            # add species name and birdcode to the current row
            row.append(speciesObject.species)
            row.append(speciesObject.birdcode)

            # add lbci, posterior median, and ubci to current row
            row.append(entry.lbci)
            row.append(entry.posterior_median)
            row.append(entry.ubci)

            # write the current row to the csv
            writer.writerow(row)

    return csvOutput
