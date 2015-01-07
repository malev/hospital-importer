import csv
import json
import os
import sys
from inflection import *
from helpers import *


class ComplicationIndicators(object):
    measures = {
        "Deaths among Patients with Serious Treatable Complications after Surgery": "death_from_serious_complications",
        "Serious complications": "serious_complications"
    }

    def __init__(self, filepath):
        self.filepath = filepath

    def provider(self, provider_number):
        output = {}
        with open(self.filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == provider_number:
                    if row[8] in self.measures:
                        output[self.measures[row[8]]] = row[10]
        return output

class AssociatedInfections(object):
    measures = {
        "Central line-associated blood stream infections (CLABSI)": "hai_1",
        "Catheter-Associated Urinary Tract Infections (CAUTI)": "hai_2",
        "Surgical Site Infection from colon surgery (SSI: Colon)": "hai_3",
        "Surgical Site Infection from abdominal hysterectomy (SSI: Hysterectomy)": "hai_4"
    }

    def __init__(self, filepath):
        self.filepath = filepath

    def provider(self, provider_number):
        output = {}
        with open(self.filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == provider_number:
                    if row[8] in self.measures:
                        key = self.measures[row[8]]
                        output[key] = parse_float(row[11])
                        output[key + "_desc"] = row[10]
        return output


class EmergencyRates(object):
    measures = ['ED_1b', 'OP_18b', 'OP_20']

    def __init__(self, filepath):
        self.filepath = filepath

    def provider(self, provider_number):
        output = {}
        with open(self.filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == provider_number:
                    for measure in self.measures:
                        if row[9] == measure:
                            output[measure.lower()] = parse_int(row[11])
        return output


class QualityIndicators(object):
    measures = [
        "H_QUIET_HSP_A_P",
        "H_QUIET_HSP_A_P",
        "H_HSP_RATING_9_10",
        "H_RECMND_DY",
        "H_COMP_2_A_P",
        "H_COMP_3_A_P",
        "H_COMP_1_A_P",
        "H_CLEAN_HSP_A_P"
        ]

    def __init__(self, filepath):
        self.filepath = filepath

    def provider(self, provider_number):
        output = {}
        with open(self.filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == provider_number:
                    print row
                    for measure in self.measures:
                        if row[8] == measure:
                            output[measure.lower()] = parse_int(row[11])
        return output


class GeneralInformation(object):
    provider_numbers = []

    def __init__(self, filepath):
        self.filepath = filepath
        self.populate()

    def hospital(self, provider_number):
        with open(self.filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == provider_number:
                    return self.parse(row)

    def parse(self, row):
        return {
            "provider_number": clean(row[0]),
            "name": clean(row[1]),
            "address": clean(row[2]),
            "city": clean(row[5]),
            "zipcode": clean(row[7]),
            "county": clean(row[8]),
            "phone_number": format_phone(row[9]),
            "type": clean(row[10]),
            "hospital ownership": clean(row[11]),
            "emergency_services": clean(row[12]),
            "latitude": get_latitude(row[13]),
            "longitude": get_longitude(row[13]),
            "url": parameterize(unicode(row[1])),
        }

    def populate(self):
        with open(self.filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.provider_numbers.append(row["Provider Number"])


def process(manifest, directory):
    hosp_file = os.path.join('./data', manifest["general_information"]["file"])
    emer_file = os.path.join(directory, manifest["emergency_care"]["file"])
    quality_file = os.path.join(directory, manifest["quality_indicators"]["file"])
    infec_file = os.path.join(directory, manifest["associated_infections"]["file"])
    comp_file = os.path.join(directory, manifest["complications_rates"]["file"])

    emergency_rates = EmergencyRates(emer_file)
    print emergency_rates.provider("450369")

    quality_indicators = QualityIndicators(quality_file)
    print quality_indicators.provider("450369")

    associated_infections = AssociatedInfections(infec_file)
    print associated_infections.provider("450369")

    complication_indicators = ComplicationIndicators(comp_file)
    print complication_indicators.provider("450369")

    # index = 1
    # general_info = GeneralInformation(hosp_file)

    # for provider_number in general_info.provider_numbers:
    #     hospital = general_info.hospital(provider_number)
    #     hospital["_id"] = index
    #     index += 1
    #     print hospital


if __name__ == '__main__':
    try:
        print "Importing"
        with open('manifest.json') as jsonfile:
            manifest = json.loads(jsonfile.read())
        process(manifest, sys.argv[1])
    except IndexError, e:
        print "You will need to specify a target directory"
        sys.exit(1)

