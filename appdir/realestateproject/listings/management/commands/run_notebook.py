from django.core.management.base import BaseCommand
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import pandas as pd
from listings.models import Listing

class Command(BaseCommand):
    help = 'Executes a Jupyter Notebook and populates the listings database'

    def handle(self, *args, **options):
        self.stdout.write("Running the Jupyter Notebook...")
        self.run_notebook("notebook/KenyanRE_1.ipynb")

    def run_notebook(self, notebook_path):
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)
            ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
            try:
                ep.preprocess(nb)
                self.stdout.write(self.style.SUCCESS('Notebook ran successfully'))
                # Assume the notebook writes its data to a CSV file
                self.populate_database("notebook/processed_data.csv")
            except Exception as e:
                self.stdout.write(self.style.ERROR('Failed to run the notebook: {}'.format(str(e))))

    def populate_database(self, data_path):
        data = pd.read_csv(data_path)
        for index, row in data.iterrows():
            listing, created = Listing.objects.update_or_create(
                id=index,  # Assuming the index of the DataFrame can serve as a unique identifier
                defaults={
                    'title': row['title'],
                    'category': row['category'],
                    'location': row['location'],
                    'beds': row['beds'],
                    'baths': row['baths'],
                    'price': row['price'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Database populated successfully'))

