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
            imported_count = 0
            null_values_count = 0  # Counter for records with null values
            for row in reader:
                data = row[0].split(';')  # Split the row data
                if len(data) != len(headers):  # Adjust the row data to match the number of headers
                    if len(data) > len(headers):
                        # Remove excess elements to match header length
                        data = data[:len(headers)]
                    else:
                        # Fill missing elements with None
                        data.extend([None] * (len(headers) - len(data)))
                # Convert empty strings to None or provide default values
                data = [None if value == '' else value for value in data]

                # Provide default values for missing required fields
                title = data[0] if data[0] else 'other'
                category = data[1] if data[1] else 'other'
                location = data[2] if data[2] else 'township'
                beds = data[3] if data[3] else 0
                baths = data[4] if data[4] else 0
                try:
                    price = int(float(data[5]))  # Truncate price to remove decimal points
                except (ValueError, TypeError):
                    price = 58000000  # Provide a default value if price is invalid or missing

                listing, created = Listing.objects.get_or_create(
                    title=title,
                    defaults={
                        'category': category,
                        'location': location,
                        'beds': beds,
                        'baths': baths,
                        'price': price,
                    }
                )
                if created:
                    imported_count += 1
                else:
                    print(f"Duplicate record found and skipped: {data}")

        total_count = Listing.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported_count} listings'))
        self.stdout.write(self.style.SUCCESS(f'Total number of listings in database: {total_count}'))
        self.stdout.write(self.style.WARNING(f'Number of records with null values: {null_values_count}'))
