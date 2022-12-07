from django.shortcuts import render
from .forms import EndpointForm, ContactForm, zoektermForm
from http.client import HTTPResponse
from unicodedata import category
from django.shortcuts import render
import pandas as pd
from lodstorage.sparql import SPARQL
from lodstorage.csv import CSV
import ssl
import json
from urllib.error import HTTPError
from urllib.request import urlopen

# Create your views here.
def home(request):
    return render (request, 'home.html')

def buildquery(request):
    if request.method == 'POST':
        form = EndpointForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['endpoints'] == True:
                endpoint = ''
            else:
                endpoint= ''
            if form.cleaned_data['dmg'] == True:
                dmg = 'FROM &lt;http://stad.gent/ldes/dmg&gt;'
            else:
                dmg= ''
            if form.cleaned_data['ag'] == True:
                ag = 'FROM &lt;http://stad.gent/ldes/archief&gt;'
            else:
                ag= ''
            if form.cleaned_data['hva'] == True:
                hva = 'FROM &lt;http://stad.gent/ldes/hva&gt;'
            else:
                hva= ''
            
            if form.cleaned_data['im'] == True:
                im = 'FROM &lt;http://stad.gent/ldes/industriemuseum&gt;'
            else:
                im= ''
            
            if form.cleaned_data['stam'] == True:
                stam = 'FROM &lt;http://stad.gent/ldes/stam&gt;'
            else:
                stam= ''
            
            if form.cleaned_data['limit'] == None:
                limit = ''
            else:
                limitnumber = str(form.cleaned_data['limit'])
                limit = 'LIMIT '+ limitnumber

            if form.cleaned_data['distinct'] == True:
                distinct = 'DISTINCT'
            else:
                distinct = ''

            if form.cleaned_data['count'] == True:
                count = 'COUNT ('
                closecount = ')'
            else:
                count = ''
                closecount = ''
            
            if form.cleaned_data['title'] == True:
                title = '?o cidoc:P102_has_title ?title.'
                variabletitle = '?title'
                if form.cleaned_data['titlefilter'] == '':
                    filtertitle = ''
                else:
                    titlefilter = form.cleaned_data['titlefilter']
                    filtertitle = 'FILTER (regex(?title, "'+titlefilter+'", "i"))'
            else:
                title= ''
                variabletitle = ''
                filtertitle = ''
            
            if form.cleaned_data['description'] == True:
                note = '?o cidoc:P3_has_note ?note.'
                variablenote = '?note'
                if form.cleaned_data['descriptionfilter'] == '':
                    filternote = ''
                else:
                    notefilter = form.cleaned_data['descriptionfilter']
                    filternote = 'FILTER (regex(?note, "'+notefilter+'", "i"))'
            else:
                note= ''
                variablenote = ''
                filternote = ''
            
            if form.cleaned_data['image'] == True:
                image = '?o cidoc:P129i_is_subject_of ?image.'
                variableimage = '?image'
            else:
                image= ''
                variableimage = ''
                   
            if form.cleaned_data['objectname'] == True:
                objectname = '''?o cidoc:P41i_was_classified_by ?classified.</br>
                ?classified cidoc:P42_assigned ?assigned.</br>
                ?assigned skos:prefLabel ?objectname.
                '''
                variableobjectname = '?objectname'
                if form.cleaned_data['objectnamefilter'] == '':
                    filterobjectname = ''
                else:
                    objectnamefilter = form.cleaned_data['objectnamefilter']
                    filterobjectname = 'FILTER (regex(?objectname, "'+objectnamefilter+'", "i"))'
            else:
                objectname = ''
                variableobjectname = ''
                filterobjectname = ''

            if form.cleaned_data['associatie'] == True:
                associatie = '''?o cidoc:P128_carries ?carries.</br>
                ?carries cidoc:P129_is_about ?about.</br>
                ?about cidoc:P2_has_type ?type.</br>
                ?type skos:prefLabel ?associatie.
                '''
                variableassociatie = '?associatie'
                if form.cleaned_data['associatiefilter'] == '':
                    filterassociatie = ''
                else:
                    associatiefilter = form.cleaned_data['associatiefilter']
                    filterassociatie = 'FILTER (regex(?associatie, "^'+associatiefilter+'$", "i"))'
            else:
                associatie = ''
                variableassociatie = ''
                filterassociatie = ''

            if form.cleaned_data['objectnumber'] == True:
                objectnumber = '''?o adms:identifier ?identifier.</br>
                ?identifier skos:notation ?objectnumber.
                '''
                variableobjectnumber = '?objectnumber'
                prefixadms = 'PREFIX adms:&lt;http://www.w3.org/ns/adms#&gt;'
                if form.cleaned_data['objectnumberfilter'] == '':
                    filterobjectnumber = ''
                else:
                    objectnumberfilter = form.cleaned_data['objectnumberfilter']
                    filterobjectnumber = 'FILTER (regex(?objectnumber, "^'+objectnumberfilter+'$", "i"))'
            else:
                objectnumber = ''
                variableobjectnumber = ''
                filterobjectnumber = ''
                prefixadms = ''

            if form.cleaned_data['vervaardiger'] == True:
                vervaardiger = '''?o cidoc:P108i_was_produced_by ?production.</br>
                ?production cidoc:P14_carried_out_by ?producer.</br>
                ?producer la:equivalent ?equivalent.</br>
                ?equivalent rdfs:label ?creator.
                '''
                variablevervaardiger = '?creator'
                if form.cleaned_data['vervaardigerfilter'] == '':
                    filtervervaardiger = ''
                else:
                    vervaardigerfilter = form.cleaned_data['vervaardigerfilter']
                    filtervervaardiger = 'FILTER (regex(?creator, "'+vervaardigerfilter+'", "i"))'
            else:
                vervaardiger = ''
                variablevervaardiger = ''
                filtervervaardiger = ''
                prefixla = ''
                        
            if form.cleaned_data['associatie'] or form.cleaned_data['objectname'] or form.cleaned_data['objectnumber']== True:
                prefix = 'PREFIX skos:&lt;http://www.w3.org/2004/02/skos/core#&gt;'
            else:
                prefix = ''
            
            if form.cleaned_data['vervaardiger'] or form.cleaned_data['plaats']== True:
                prefixla = 'PREFIX la:&lt;https://linked.art/ns/terms/&gt;'
            else:
                prefixla = ''

            if form.cleaned_data['datum'] == True:
                datum = '''?o cidoc:P108i_was_produced_by ?produced.</br>
                ?produced cidoc:P4_has_time-span ?timespan.</br>
                '''
                variabledatum = '?timespan'
                if form.cleaned_data['datumfilter'] == '':
                    filterdatum = ''
                else:
                    datumfilter = form.cleaned_data['datumfilter']
                    filterdatum = 'FILTER (regex(?timespan, "'+datumfilter+'", "i"))'
            else:
                datum = ''
                variabledatum = ''
                filterdatum = ''

            if form.cleaned_data['techniek'] == True:
                techniek = '''?o cidoc:P108i_was_produced_by ?produced.</br>
                ?produced cidoc:P32_used_general_technique ?technique.</br>
                ?technique cidoc:P2_has_type ?hastype.</br>
                ?hastype skos:prefLabel ?techniek.</br>
                '''
                variabletechniek = '?techniek'
                if form.cleaned_data['techniekfilter'] == '':
                    filtertechniek = ''
                else:
                    techniekfilter = form.cleaned_data['techniekfilter']
                    filtertechniek = 'FILTER (regex(?techniek, "'+techniekfilter+'", "i"))'
            else:
                techniek = ''
                variabletechniek = ''
                filtertechniek = ''
            
            if form.cleaned_data['materiaal'] == True:
                materiaal = '''?o cidoc:P45_consists_of ?consists.</br>
                ?consists cidoc:P2_has_type ?materiaaltype.</br>
                ?materiaaltype skos:prefLabel ?materiaal.</br>
                '''
                variablemateriaal = '?materiaal'
                if form.cleaned_data['materiaalfilter'] == '':
                    filtermateriaal = ''
                else:
                    materiaalfilter = form.cleaned_data['materiaalfilter']
                    filtermateriaal = 'FILTER (regex(?materiaal, "'+materiaalfilter+'", "i"))'
            else:
                materiaal = ''
                variablemateriaal = ''
                filtermateriaal = ''

            if form.cleaned_data['plaats'] == True:
                plaats = '''?o cidoc:P108i_was_produced_by ?produced.</br>
                ?produced cidoc:P7_took_place_at ?tookplace.</br>
                ?tookplace la:equivalent ?plaatsequivalent.</br>
                ?plaatsequivalent skos:prefLabel ?plaats.</br>
                '''
                variableplaats = '?plaats'
                if form.cleaned_data['plaatsfilter'] == '':
                    filterplaats = ''
                else:
                    plaatsfilter = form.cleaned_data['plaatsfilter']
                    filterplaats = 'FILTER (regex(?plaats, "'+plaatsfilter+'", "i"))'
            else:
                plaats = ''
                variableplaats = ''
                filterplaats = ''
           
            return render(request, 'query.html', {'endpoint': endpoint, 'hva': hva, 'dmg': dmg, 'im': im, 'ag': ag, 'stam': stam, 
            'limit': limit, 'distinct': distinct, 'count': count, 'closecount': closecount,
            'variabletitle': variabletitle, 'title': title, 'filtertitle': filtertitle, 
            'note': note, 'variablenote': variablenote, 'filternote': filternote, 
            'image': image, 'variableimage': variableimage, 
            'prefix': prefix, 'prefixadms': prefixadms, 'prefixla': prefixla,
            'objectname': objectname, 'variableobjectname': variableobjectname, 'filterobjectname': filterobjectname, 
            'associatie': associatie, 'variableassociatie': variableassociatie, 'filterassociatie': filterassociatie,
            'objectnumber': objectnumber, 'variableobjectnumber': variableobjectnumber, 'filterobjectnumber': filterobjectnumber,
            'vervaardiger': vervaardiger, 'variablevervaardiger': variablevervaardiger, 'filtervervaardiger': filtervervaardiger,
            'datum': datum, 'variabledatum': variabledatum, 'filterdatum': filterdatum,
            'techniek': techniek, 'variabletechniek': variabletechniek, 'filtertechniek': filtertechniek,
            'materiaal': materiaal, 'variablemateriaal': variablemateriaal, 'filtermateriaal': filtermateriaal,
            'plaats': plaats, 'variableplaats': variableplaats, 'filterplaats': filterplaats})
            
    form = EndpointForm()
   
    return render(request, 'form.html', {'form':form})

def getldes(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            objectnumber = form.cleaned_data['objectnumber']
            institution = form.cleaned_data['institution']

            if institution == 'archief':
                ssl._create_default_https_context = ssl._create_unverified_context

                sparqlQuery = """
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    PREFIX adms: <http://www.w3.org/ns/adms#>
                    PREFIX prov: <http://www.w3.org/ns/prov#>
                    SELECT DISTINCT ?ldes FROM <http://stad.gent/ldes/""" + institution + """> 
                    WHERE { 
                    ?object adms:identifier ?identifier.
                    ?identifier skos:notation ?objectnumber.
                    FILTER (regex(?objectnumber,""" + ' "^' + objectnumber + '$"' + """, "i")).
                    ?object prov:generatedAtTime ?time.
                    BIND(URI(concat("https://apidg.gent.be/opendata/adlib2eventstream/v1/"""+ "archiefgent" +"""/objecten?generatedAtTime=", ?time)) AS ?ldes)
                    } ORDER BY DESC(?object)
                    """

                df_sparql = pd.DataFrame()
                sparql = SPARQL("https://stad.gent/sparql")
                qlod = sparql.queryAsListOfDicts(sparqlQuery)
                if qlod == []:
                    return render(request, 'error.html')
                else:
                    csv = CSV.toCSV(qlod)
                    df_result = pd.DataFrame([x.split(',') for x in csv.split('\n')])
                    df_sparql = df_sparql.append(df_result, ignore_index=True)
                    df_sparql[0] = df_sparql[0].str.replace(r'"', '')
                    ldes = df_sparql[0].iloc[1]
                    return render(request, 'ldes.html', {'ldes': ldes})
            
            else:
                ssl._create_default_https_context = ssl._create_unverified_context

                sparqlQuery = """
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    PREFIX adms: <http://www.w3.org/ns/adms#>
                    PREFIX prov: <http://www.w3.org/ns/prov#>
                    SELECT DISTINCT ?ldes FROM <http://stad.gent/ldes/""" + institution + """> 
                    WHERE { 
                    ?object adms:identifier ?identifier.
                    ?identifier skos:notation ?objectnumber.
                    FILTER (regex(?objectnumber,""" + ' "^' + objectnumber + '$"' + """, "i")).
                    ?object prov:generatedAtTime ?time.
                    BIND(URI(concat("https://apidg.gent.be/opendata/adlib2eventstream/v1/"""+ institution +"""/objecten?generatedAtTime=", ?time)) AS ?ldes)
                    } ORDER BY DESC(?object)
                    """

                df_sparql = pd.DataFrame()
                sparql = SPARQL("https://stad.gent/sparql")
                qlod = sparql.queryAsListOfDicts(sparqlQuery)
                if qlod == []:
                    return render(request, 'error.html')
                else:
                    csv = CSV.toCSV(qlod)
                    df_result = pd.DataFrame([x.split(',') for x in csv.split('\n')])
                    df_sparql = df_sparql.append(df_result, ignore_index=True)
                    df_sparql[0] = df_sparql[0].str.replace(r'"', '')
                    ldes = df_sparql[0].iloc[1]
                    return render(request, 'ldes.html', {'ldes': ldes})

    form = ContactForm()
    return render(request, 'formldes.html', {'form':form})

def iiifmanifest():
    ssl._create_default_https_context = ssl._create_unverified_context

    sparqlQuery = """
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    SELECT ?o WHERE {
    ?s cidoc:P129i_is_subject_of ?o .
    BIND(RAND() AS ?random) .
    } ORDER BY ?random
    LIMIT 1
    """

    df_sparql = pd.DataFrame()
    sparql = SPARQL("https://stad.gent/sparql")
    qlod = sparql.queryAsListOfDicts(sparqlQuery)
    csv = CSV.toCSV(qlod)
    df_result = pd.DataFrame([x.split(',') for x in csv.split('\n')])
    df_sparql = df_sparql.append(df_result, ignore_index=True)
    df_sparql[0] = df_sparql[0].str.replace(r'"', '')
    df_sparql[0] = df_sparql[0].str.replace(r'\r', '')

    iiifmanifest = df_sparql[0].iloc[1]
    return iiifmanifest

def image(request):
    manifest = iiifmanifest()
    try:
        response = urlopen(manifest)
    except ValueError:
        return image(request)
    except HTTPError:
        return image(request)
    else:
        data_json = json.loads(response.read())
        iiif_manifest = data_json["sequences"][0]['canvases'][0]["images"][0]["resource"]["@id"]
        license = data_json["sequences"][0]['canvases'][0]['images'][0]['license']
        label = data_json["label"]['@value']
        objectnumber = data_json['@id']
        label = data_json["label"]['@value']          
        if 'stam' in manifest:
            objectnumber = objectnumber.split("stam:", 1)[1]
            webplatform = 'https://data.collectie.gent/entity/stam:' + objectnumber
            instelling = 'STAM'
        elif 'hva' in manifest:
            objectnumber = objectnumber.split("hva:", 1)[1]
            webplatform = 'https://data.collectie.gent/entity/hva:' + objectnumber
            instelling = 'Huis van Alijn'
        elif 'dmg' in manifest:
            objectnumber = objectnumber.split("dmg:", 1)[1]
            webplatform = 'https://data.collectie.gent/entity/dmg:' + objectnumber
            instelling = 'Design Museum Gent'
        elif 'industriemuseum' in manifest:
            objectnumber = objectnumber.split("industriemuseum:", 1)[1]
            webplatform = 'https://data.collectie.gent/entity/industriemuseum:' + objectnumber
            instelling = 'Industriemuseum'
        else:
            objectnumber = objectnumber.split("archiefgent:", 1)[1]
            webplatform = 'https://data.collectie.gent/entity/archiefgent:' + objectnumber
            instelling = 'Archief Gent'
        return render(request, 'image.html', {'iiif_manifest': iiif_manifest, 'instelling': instelling, 'label': label, 'license': license, 'webplatform': webplatform})

def collage(request):
    if request.method == 'POST':
        form = zoektermForm(request.POST)
        if form.is_valid():
            zoekterm = form.cleaned_data['zoekterm']
            ssl._create_default_https_context = ssl._create_unverified_context

            sparqlQuery = """
             PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
             SELECT DISTINCT ?o ?title WHERE {
             ?object cidoc:P129i_is_subject_of ?o .
             ?object cidoc:P102_has_title ?title.
             FILTER (regex(?title, """ + ' "' + zoekterm + '" ' + """ , "i"))
             BIND(RAND() AS ?random) .
             } ORDER BY ?random
             LIMIT 20
             """

            sparql = SPARQL("https://stad.gent/sparql")
            qlod = sparql.queryAsListOfDicts(sparqlQuery)

            
            if len(qlod) == 0:
                return render(request, 'error2.html')
            else:
                iiif_manifests = []
                webplatform_links = []
                titels = []
                for i in range(0, len(qlod)):
                    try:
                        response = urlopen(qlod[i]['o'])
                    except ValueError:
                        pass
                    except HTTPError:
                        pass
                    else:
                        data_json = json.loads(response.read())
                        afbeelding = data_json["sequences"][0]['canvases'][0]["images"][0]["resource"]["@id"]
                        afbeelding = afbeelding.replace("full/full/0/default.jpg", "square/1000,/0/default.jpg")
                        manifestje = data_json["@id"]
                        objectnummer = manifestje.rpartition('/')[2]
                        webplatform = "https://data.collectie.gent/entity/" + objectnummer
                        titel = data_json["label"]['@value']
                        iiif_manifests.append(afbeelding)
                        webplatform_links.append(webplatform)
                        titels.append(titel)
             

                if len(iiif_manifests) > 9:
                    iiif_manifests = iiif_manifests[:9]
                    data = zip(iiif_manifests, webplatform_links, titels)
                    print(data)
                    return render (request, 'collage.html', {'form': form, 'data':data})
                else:
                    data = zip(iiif_manifests, webplatform_links, titels)
                    return render (request, 'collage.html', {'form': form, 'data':data})
        else:
            return render(request, 'error2.html')
    form = zoektermForm
    return render(request, 'collage.html', {'form': form})