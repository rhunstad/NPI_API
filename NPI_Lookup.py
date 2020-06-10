"""
PROJECT NOTES:

6/9/2020 - Ryland Hunstad:
    - I developed this script to match the data from Qlik that was missing NPI numbers for the doctors, from both the
    Pain prescribers and Sleep prescribers data set that Symphony provided Galt with
    - I found the following code, and modified it to my needs, at this GitHub repository:
    https://github.com/ricfield/npi_lt and copied the 33 lines in the npi_lt.py file

    - This API script is also, with some configuring, able to grab phone/fax, Y/N sole proprietor, credential/credential
    date, identifier, taxonomies, and multiple addresses (all in addition to grabbing the NPI) if need be

6/10/2020 - Ryland Hunstad:
    After getting this script working properly, it seemed to only draw a couple names (of 9,615 missing NPI numbers,
    it was only able to successfully match about 50) and after investigating on https://npiregistry.cms.hhs.gov/api/demo?version=2.0
    I found that for those doctors, all of them weren't even in the system. I.e., when looking up a doctor's name,
    even without limiting search results by any metric, their name was not in the NPI system.

    That being said, this script should still work but its usefulness is questionable, due to the lack of NPI data
"""

import urllib.request
import json
import pandas as pd
import numpy as np
import math
input_valid = True


def main():
    painReport = pd.read_csv("PainReportCSV.csv", low_memory=False)
    # accountExport = pd.read_csv("AccountExportCSV.csv", low_memory=False)
    # sleepReport = pd.read_csv("SleepReport-CorrectCSV.csv", low_memory=False)
    not_found = []
    too_many = []
    found_count = 0
    count = 0
    for index, row in painReport.iterrows():
        count += 1
        if math.isnan(row.npiNum):
            npi_query = getNPIInformationJSON(row.Fname, row.Lname, row.zipcode)
            if npi_query["result_count"] == 0:
                not_found += [(row.Fname, row.Lname, row.zipcode)]
            elif npi_query["result_count"] == 1:
                row.npiNum = npi_query["results"][0]["number"]
                print("%s, %s, %s, %s" % (row.Fname, row.Lname, row.zipcode, row.npiNum))
            elif npi_query["result_count"] > 1:
                too_many += [row.Fname, row.Lname, row.zipcode]

    print("\n\n\n\n\n")
    print(found_count)
    print(not_found)
    print(too_many)

    pv_information_json = getNPIInformationJSON("James", "Douglas", "30161")
    print(pv_information_json["results"][0]["number"])


def getNPIInformationJSON(first_name, last_name, zip_code):
    url = "https://npiregistry.cms.hhs.gov/api/?number=&enumeration_type=&taxonomy_description=&first_name=%s&last_name=%s&organization_name=&address_purpose=&city=&state=&postal_code=%s&country_code=&limit200=&skip=&version=2.0" % (
        first_name, last_name, zip_code)
    nppes_url = urllib.request.urlopen(url)
    providerJSONData = json.loads(nppes_url.read())
    return providerJSONData


if __name__ == '__main__':
    main()
