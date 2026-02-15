import random
from django.core.management.base import BaseCommand
from elections.models import Position, Candidate
from django.core.files.base import ContentFile
import urllib.request

class Command(BaseCommand):
    help = 'Creates mock data for positions and candidates.'

    def handle(self, *args, **options):
        self.stdout.write("Deleting old data...")
        Candidate.objects.all().delete()
        Position.objects.all().delete()

        self.stdout.write("Creating new data...")

        positions = [
            "President", "Vice President", "General Secretary", "Financial Secretary",
            "Publicity Secretary", "Social Director", "Welfare Officer", "Sports Director",
            "Academic Director"
        ]

        first_names = ["John", "Jane", "Peter", "Mary", "David", "Susan", "Michael", "Linda"]
        last_names = ["Smith", "Jones", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore"]

        for pos_name in positions:
            position, created = Position.objects.get_or_create(name=pos_name)
            self.stdout.write(f'Created position: {position.name}')
            for i in range(random.randint(2, 4)):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                matric = f"F/HD/23/3740{random.randint(100, 999)}"
                
                candidate = Candidate(
                    first_name=first_name,
                    last_name=last_name,
                    matric=matric,
                    position=position,
                    manifesto=f"This is the manifesto of {first_name} {last_name}. I will do my best for the department."
                )

                # Fetch a random image and save it
                try:
                    url = f"https://picsum.photos/400/300?random={random.randint(1, 1000)}"
                    with urllib.request.urlopen(url) as response:
                        image_data = response.read()
                        file_name = f"{matric.replace('/', '_')}.jpg"
                        candidate.photo.save(file_name, ContentFile(image_data), save=True)
                    
                    self.stdout.write(f'  Created candidate: {candidate} with image.')

                except Exception as e:
                    self.stderr.write(f"Error fetching image for {candidate}: {e}")
                    # Create candidate without image if image fetching fails
                    candidate.save()
                    self.stdout.write(f'  Created candidate: {candidate} without image.')


        self.stdout.write(self.style.SUCCESS("Mock data created successfully."))
