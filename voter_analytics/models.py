from django.db import models
import csv
from datetime import datetime
from django.conf import settings
import os

class Voter(models.Model):
    # Personal Information
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=50)
    precinct_number = models.CharField(max_length=10)

    # Address Information
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=100)
    apartment_number = models.CharField(max_length=10, blank=True, null=True)
    zip_code = models.CharField(max_length=10)

    # Voter Participation in Elections
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    voter_score = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Precinct {self.precinct_number}"
def load_data():
    csv_file_path = os.path.join(settings.BASE_DIR, 'newton_voters.csv')

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        voters = []
        for row in reader:
            #print(f'Processing row: {row}')
            date_of_birth = datetime.strptime(row['Date of Birth'], '%Y-%m-%d').date()
            date_of_registration = datetime.strptime(row['Date of Registration'], '%Y-%m-%d').date()

            v20state = row['v20state'].strip() == 'TRUE'
            v21town = row['v21town'].strip() == 'TRUE'
            v21primary = row['v21primary'].strip() == 'TRUE'
            v22general = row['v22general'].strip() == 'TRUE'
            v23town = row['v23town'].strip() == 'TRUE'

            # Create Voter instance
            voter = Voter(
                last_name=row['Last Name'],
                first_name=row['First Name'],
                date_of_birth=date_of_birth,
                date_of_registration=date_of_registration,
                party_affiliation=row['Party Affiliation'],
                precinct_number=row['Precinct Number'],
                street_number=row['Residential Address - Street Number'],
                street_name=row['Residential Address - Street Name'],
                apartment_number=row.get('Residential Address - Apartment Number', '').strip() or None,
                zip_code=row['Residential Address - Zip Code'],
                v20state=v20state,
                v21town=v21town,
                v21primary=v21primary,
                v22general=v22general,
                v23town=v23town,
                voter_score=int(row['voter_score']),
            )
            #print(f'Created result: {voter}')
            voter.save()