import csv
from django.core.management.base import BaseCommand
from nyumba.models import Listing

csv_file = '/Users/wepukhulu/Desktop/Directory/yr4/Final-yrProject/processed_data.csv'

class Command(BaseCommand):
    help = 'Import listings from a CSV file'

    def handle(self, *args, **kwargs):
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)[0].split(';')  # Read and split the first row
            print(headers)  # Check if headers are correct
            for row in reader:
                data = row[0].split(';')  # Split the row data
                if len(data) == len(headers):  # Check if number of elements match
                    # Convert empty strings to None or provide default values
                    data = [None if value == '' else value for value in data]
                    # Check if required fields are not empty
                    if data[0] and data[5]:  # Assuming title and price are required
                        listing = Listing(
                            title=data[0],
                            category=data[1],
                            location=data[2],
                            beds=data[3],
                            baths=data[4] if data[4] else None,  # Convert empty baths to None
                            price=data[5]
                        )
                        listing.save()
                    else:
                        print("Skipping row with missing required fields:", row)
                else:
                    print("Skipping row with incorrect number of elements:", row)
        self.stdout.write(self.style.SUCCESS('Successfully imported listings'))
