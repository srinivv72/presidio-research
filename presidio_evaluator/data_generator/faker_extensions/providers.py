import random
import warnings
from collections import OrderedDict
from pathlib import Path
import socket
from typing import Union, List
import yaml
import requests
from functools import reduce

import pandas as pd
from faker.providers import BaseProvider
from faker.providers.address.en_US import Provider as AddressProvider
from faker.providers.phone_number.en_US import Provider as PhoneNumberProvider

from presidio_evaluator.data_generator import raw_data_dir


class NationalityProvider(BaseProvider):
    def __init__(self, generator, nationality_file: Union[str, Path] = None):
        super().__init__(generator=generator)
        if not nationality_file:
            nationality_file = (raw_data_dir / "nationalities.csv").resolve()

        self.nationality_file = nationality_file
        self.nationalities = self.load_nationalities()

    def load_nationalities(self):
        return pd.read_csv(self.nationality_file)

    def country(self):
        self.random_element(self.nationalities["country"].tolist())

    def nationality(self):
        return self.random_element(self.nationalities["nationality"].tolist())

    def nation_man(self):
        return self.random_element(self.nationalities["man"].tolist())

    def nation_woman(self):
        return self.random_element(self.nationalities["woman"].tolist())

    def nation_plural(self):
        return self.random_element(self.nationalities["plural"].tolist())


class OrganizationProvider(BaseProvider):
    def __init__(
        self,
        generator,
        organizations_file: Union[str, Path] = None,
    ):
        super().__init__(generator=generator)
        if not organizations_file:
            # company names assembled from stock exchange listings (aex, bse, cnq, ger, lse, nasdaq, nse, nyse, par, tyo),
            # US government websites like https://www.sec.gov/rules/other/4-460list.htm, and other sources
            organizations_file = Path(
                Path(__file__).parent.parent,
                "raw_data",
                "companies_and_organizations.csv",
            ).resolve()
        self.organizations_file = organizations_file
        self.organizations = self.load_organizations()

    def load_organizations(self):
        return pd.read_csv(self.organizations_file, delimiter="\t")

    def organization(self):
        return self.random_element(self.organizations["organization"].tolist())

    def company(self):
        return self.organization()


class UsDriverLicenseProvider(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator=generator)
        us_driver_license_file = Path(
            Path(__file__).parent.parent, "raw_data", "us_driver_license_format.yaml"
        ).resolve()
        formats = yaml.safe_load(open(us_driver_license_file))
        self.formats = formats["en"]["faker"]["driving_license"]["usa"]

    def us_driver_license(self) -> str:
        # US driver's licenses patterns vary by state. Here we sample a random state and format
        us_state = random.choice(list(self.formats))
        us_state_format = random.choice(self.formats[us_state])
        return self.bothify(text=us_state_format)


class ReligionProvider(BaseProvider):
    def __init__(
        self,
        generator,
        religions_file: Union[str, Path] = None,
    ):
        super().__init__(generator=generator)
        if not religions_file:
            religions_file = Path(
                Path(__file__).parent.parent, "raw_data", "religions.csv"
            ).resolve()
        self.religions_file = religions_file
        self.religions = self.load_religions()

    def load_religions(self):
        return pd.read_csv(self.religions_file, delimiter="\t")

    def religion(self) -> str:
        """Return a random (major) religion."""
        return self.random_element(self.religions["Religions"].tolist())


class IpAddressProvider(BaseProvider):
    """Generating both v4 and v6 IP addresses."""

    def ip_address(self):
        if random.random() < 0.8:
            return self.generator.ipv4()
        else:
            return self.generator.ipv6()


class AgeProvider(BaseProvider):
    formats = OrderedDict(
        [
            ("%#", 0.8),
            ("%", 0.1),
            ("1.%", 0.02),
            ("2.%", 0.02),
            ("100", 0.02),
            ("101", 0.01),
            ("104", 0.01),
            ("0.%", 0.02),
        ]
    )

    def age(self):
        return self.numerify(
            self.random_elements(elements=self.formats, length=1, use_weighting=True)[0]
        )


class AddressProviderNew(AddressProvider):
    """
    Extending the Faker AddressProvider with additional templates
    """

    address_formats = OrderedDict(
        (
            (
                "{{building_number}} {{street_name}} {{secondary_address}} {{city}} {{state}}",
                5.0,
            ),
            (
                "{{building_number}} {{street_name}} {{secondary_address}} {{city}} {{state_abbr}}",
                5.0,
            ),
            (
                "{{building_number}} {{street_name}} {{secondary_address}} {{city}} {{country}}",
                5.0,
            ),
            (
                "{{building_number}} {{street_name}}\n {{secondary_address}}\n {{city}}\n {{country}}",
                5.0,
            ),
            (
                "{{building_number}} {{street_name}}\n {{secondary_address}}\n {{city}}\n {{country}} {{postcode}}",
                5.0,
            ),
            (
                "{{street_name}} {{street_name}}\n {{secondary_address}}\n {{city}}\n {{country}} {{postcode}}",
                5.0,
            ),
            ("the corner of {{street_name}} and {{street_name}}", 3.0),
            ("{{first_name}} and {{street_name}}", 3.0),
            ("{{street_address}}, {{city}}, {{country}}", 5.0),
            (
                "{{street_address}} {{secondary_address}}, {{city}}, {{country}} {{postcode}}",
                5.0,
            ),
            ("{{street_address}}\n{{city}}, {{state_abbr}} {{postcode}}", 25.0),
            ("{{street_address}}\n{{city}}\n, {{state_abbr}}\n {{postcode}}", 25.0),
            (
                "{{street_address}}\n{{city}}\n, {{state_abbr}}\n {{country}} {{postcode}}",
                25.0,
            ),
            #  military address formatting.
            ("{{military_apo}}\nAPO {{military_state}} {{postcode}}", 1.0),
            (
                "{{military_ship}} {{last_name}}\nFPO {{military_state}} {{postcode}}",
                1.0,
            ),
            ("{{military_dpo}}\nDPO {{military_state}} {{postcode}}", 1.0),
        )
    )


class PhoneNumberProviderNew(PhoneNumberProvider):
    """
    Similar to the default PhoneNumberProvider, with different formats
    """

    formats = (
        # US
        "##########",
        "##########",
        "###-###-####",
        "###-###-####",
        "###-#######",
        # UK
        "07700 ### ###",
        "07700 ######",
        "07700######",
        "(07700) ### ###",
        "(07700) ######",
        "(07700)######",
        "+447700 ### ###",
        "+447700 ######",
        "+447700######",
        # India
        "+91##########",
        "0##########",
        "##########",
        # Switzerland
        "+41 2# ### ## ##",
        "+41 3# ### ## ##",
        "+41 4# ### ## ##",
        "+41 5# ### ## ##",
        "+41 6# ### ## ##",
        "+41 7# ### ## ##",
        "+41 8# ### ## ##",
        "+41 9# ### ## ##",
        "+41 (0)2# ### ## ##",
        "+41 (0)3# ### ## ##",
        "+41 (0)4# ### ## ##",
        "+41 (0)5# ### ## ##",
        "+41 (0)6# ### ## ##",
        "+41 (0)7# ### ## ##",
        "+41 (0)8# ### ## ##",
        "+41 (0)9# ### ## ##",
        "+46 (0)8 ### ### ##",
        "+46 (0)## ## ## ##",
        "+46 (0)### ### ##",
        # Optional 10-digit local phone number format
        "(###)###-####",
        "(###)###-####",
        "(###)###-####",
        "(###)###-####",
        # Non-standard 10-digit phone number format
        "###.###.####",
        "###.###.####",
        # Standard 10-digit phone number format with extensions
        "###-###-####x###",
        "###-###-####x####",
        # Optional 10-digit local phone number format with extensions
        "(###)###-####x###",
        "(###)###-####x####",
        # Non-standard 10-digit phone number format with extensions
        "###.###.####x###",
        "###.###.####x####",
        # Standard 11-digit phone number format
        "+1-###-###-####",
        "001-###-###-####",
        # Standard 11-digit phone number format with extensions
        "+1-###-###-####x###",
    )


class HospitalProvider(BaseProvider):
    def __init__(self, generator, hospital_file: str = None):
        """Load hospital data from file or wiki.

        :param hospital_file: Path to static file containing hospital names
        """

        super().__init__(generator=generator)

        self.default_list = [
            "Apollo Hospital",
            "St. Peter",
            "Mount Sinai",
            "Providence",
        ]
        self.hospitals = self.load_hospitals(hospital_file)

    def load_hospitals(self, hospital_file: str) -> List[str]:
        """Loads a list of hospital names based in the US.
        If a static file with hospital names is provided,
        the hospital names should be under a column named "name".
        If no file is provided, the information will be retrieved from WikiData.

        :param hospital_file: Path to static file containing hospital names
        """

        if hospital_file:
            hospitals = pd.read_csv(hospital_file)
            if "name" not in self.hospitals:
                print(
                    "Unable to retrieve hospital names, "
                    "file is missing column named 'name'"
                )
                return self.default_list
            return hospitals["name"].to_list()
        else:
            return self.load_wiki_hospitals()

    def hospital_name(self):
        return self.random_element(self.hospitals)

    def load_wiki_hospitals(
        self,
    ):
        """Executes a query on WikiData and extracts a list of US based hospitals"""
        url = "https://query.wikidata.org/sparql"
        query = """
        SELECT DISTINCT ?label_en
        WHERE 
        { ?item wdt:P31/wdt:P279* wd:Q16917; wdt:P17 wd:Q30
        OPTIONAL { ?item p:P31/ps:P31 wd:Q64578911 . BIND(wd:Q64578911 as ?status1) } BIND(COALESCE(?status1,wd:Q64624840) as ?status)
        OPTIONAL { ?item wdt:P131/wdt:P131* ?ac . ?ac wdt:P5087 [] }
        optional { ?item rdfs:label ?label_en FILTER((LANG(?label_en)) = "en") }   
        }

        """
        try:
            r = requests.get(url, params={"format": "json", "query": query})
            if r.status_code != 200:
                print("Unable to read hospitals from WikiData, returning an empty list")
                return self.default_list
            data = r.json()
            bindings = data["results"].get("bindings", [])
            hospitals = [self.deep_get(x, ["label_en", "value"]) for x in bindings]
            hospitals = [x for x in hospitals if "no key" not in x]
            return hospitals
        except socket.error:
            warnings.warn("Can't download hospitals data. Returning default list")
            return self.default_list

    def deep_get(self, dictionary: dict, keys: List[str]):
        """Retrieve values from a nested dictionary for specific nested keys
        > example:
        > d = {"key_a":1, "key_b":{"key_c":2}}
        > deep_get(d, ["key_b","key_c"])
        > ... 2

        > deep_get(d, ["key_z"])
        > ... "no key key_z"
        :param dictionary: Nested dictionary to search for keys
        :type dictionary: dict
        :param keys: list of keys, each value should represent the next level of nesting
        :type keys: List
        :return: The value of the nested keys
        """

        return reduce(
            lambda dictionary, key: dictionary.get(key, f"no key {key}")
            if isinstance(dictionary, dict)
            else f"no key {key}",
            keys,
            dictionary,
        )


class MedicalProvider(BaseProvider):
    def drug(self):
        drugs = [
            "Ibuprofen", "Paracetamol", "Metformin", "Atorvastatin", "Amlodipine",
            "Lisinopril", "Simvastatin", "Levothyroxine", "Omeprazole", "Amoxicillin",
            "Azithromycin", "Hydrochlorothiazide", "Albuterol", "Gabapentin",
            "Losartan", "Sertraline", "Prednisone", "Ciprofloxacin", "Warfarin",
            "Metoprolol", "Insulin", "Furosemide", "Clopidogrel", "Citalopram",
            "Fluoxetine"
        ]
        return self.random_element(drugs)
    def medical_condition(self):
        conditions = [
            "Hypertension", "Diabetes Mellitus", "Asthma", "Chronic Obstructive Pulmonary Disease",
            "Coronary Artery Disease", "Hypothyroidism", "Rheumatoid Arthritis", "Osteoarthritis",
            "Epilepsy", "Migraine", "Anxiety Disorder", "Depression", "Heart Failure",
            "Chronic Kidney Disease", "Gastroesophageal Reflux Disease", "Psoriasis",
            "Tuberculosis", "Pneumonia", "Anemia", "Hyperlipidemia", "Bronchitis",
            "Urinary Tract Infection", "Hepatitis B", "Hepatitis C", "Atrial Fibrillation"
        ]
        return self.random_element(conditions)
    def symptom(self):
        symptoms = [
            "Headache", "Fever", "Cough", "Fatigue", "Shortness of Breath", "Chest Pain",
            "Nausea", "Vomiting", "Dizziness", "Back Pain", "Abdominal Pain", "Sore Throat",
            "Joint Pain", "Muscle Weakness", "Rash", "Blurred Vision", "Palpitations",
            "Loss of Appetite", "Insomnia", "Diarrhea", "Constipation", "Swelling",
            "Weight Loss", "Night Sweats"
        ]
        return self.random_element(symptoms)
    def procedure(self):
        procedures = [
            "MRI", "CT Scan", "Blood Test", "X-ray", "Ultrasound", "Echocardiogram",
            "Colonoscopy", "Endoscopy", "Electrocardiogram", "Biopsy", "Vaccination",
            "Physical Therapy", "Dialysis", "Coronary Angioplasty", "Appendectomy",
            "Cataract Surgery", "Chemotherapy", "Radiation Therapy", "Mammogram",
            "Pap Smear", "Laparoscopy", "Bronchoscopy", "Pacemaker Implantation"
        ]
        return self.random_element(procedures)

    def dosage(self, medication_type: str = None) -> str:
        """Generate a realistic medication dosage.
        
        Args:
            medication_type: Optional specific type of medication (e.g., 'tablet', 'injection')
            
        Returns:
            str: Formatted dosage string (e.g., "500 mg tablet")
        """
        # Common dosage forms
        forms = {
            'tablet': ['mg', 'mcg'],
            'capsule': ['mg', 'mcg', 'IU'],
            'injection': ['mg/mL', 'units/mL', 'mcg/mL', '%'],
            'solution': ['mg/5mL', 'mg/mL', '%'],
            'cream': ['%', 'mg/g'],
            'inhaler': ['mcg/dose', 'mg/dose'],
            'drops': ['%', 'mg/mL'],
            'suppository': ['mg', 'mcg'],
            'patch': ['mg/h', 'mcg/h'],
        }
        
        # If no specific form is provided, select one randomly
        if not medication_type:
            medication_type = self.random_element(list(forms.keys()))
        
        # Get appropriate units for the form
        units = forms.get(medication_type, ['mg', 'mcg', 'units'])
        unit = self.random_element(units)
        
        # Generate appropriate dosage based on unit
        if unit == 'mg':
            # Common mg dosages
            dosages = [str(x) for x in [1, 2.5, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 
                                    75, 100, 125, 150, 200, 250, 300, 400, 500, 600, 
                                    750, 800, 1000]]
        elif unit == 'mcg' or unit == 'mcg/dose' or unit == 'mcg/h':
            # Common mcg dosages
            dosages = [str(x) for x in [5, 10, 20, 25, 50, 75, 100, 125, 150, 200, 250, 
                                    300, 400, 500, 600, 800, 1000]]
        elif unit == 'IU':
            # Common IU dosages (for vitamins, some hormones)
            dosages = [str(x) for x in [100, 200, 400, 500, 1000, 2000, 5000, 10000, 50000]]
        elif unit == 'mg/mL' or unit == 'mg/5mL':
            # Common concentrations for liquids
            dosages = [str(x) for x in [1, 2, 2.5, 5, 10, 12.5, 15, 20, 25, 40, 50, 80, 100, 125, 200, 250]]
        elif unit == 'units/mL':
            # For insulin and similar
            dosages = [str(x) for x in [100, 200, 500, 1000]]
        elif unit == '%':
            # For creams and solutions
            dosages = [f"0.0{x}" for x in range(1, 10)] + [f"0.{x}" for x in range(1, 10)] + [str(x) for x in range(1, 11)]
        else:
            # Default case
            dosages = [str(x) for x in range(1, 11)]
        
        # Select a random dosage
        dosage = self.random_element(dosages)
        
        # Format the output
        return f"{dosage}{unit} {medication_type}" if medication_type else f"{dosage}{unit}"


    def drug_frequency(self):
        frequencies = [
            "once daily",
            "twice daily",
            "three times daily",
            "four times daily",
            "every 4 hours as needed",
            "every 6 hours as needed",
            "every 8 hours",
            "every 12 hours",
            "every morning",
            #"at bedtime",
            "every other day",
            "weekly",
            "monthly",
            #"as directed",
            #"before meals",
            #"after meals",
            #"with food",
            #"on an empty stomach"
        ]
        return self.random_element(frequencies)

    def lab_test(self):
        """Generate a random lab test name."""
        lab_tests = {
            # Blood Tests
            "CBC (Complete Blood Count)": "Blood",
            "Basic Metabolic Panel (BMP)": "Blood",
            "Comprehensive Metabolic Panel (CMP)": "Blood",
            "Lipid Panel": "Blood",
            "Liver Function Tests (LFTs)": "Blood",
            "Thyroid Function Tests (TFTs)": "Blood",
            "Hemoglobin A1C": "Blood",
            "Blood Glucose (Fasting)": "Blood",
            "Electrolyte Panel": "Blood",
            "Coagulation Panel (PT/INR, PTT)": "Blood",
            
            # Urine Tests
            "Urinalysis (UA)": "Urine",
            "Urine Culture": "Urine",
            "24-hour Urine Protein": "Urine",
            "Microalbumin/Creatinine Ratio": "Urine",
            "Urine Drug Screen": "Urine",
            "Urine Pregnancy Test": "Urine",
            
            # Cardiac Markers
            "Troponin": "Blood",
            "BNP (B-type Natriuretic Peptide)": "Blood",
            "CK-MB (Creatine Kinase-MB)": "Blood",
            "Myoglobin": "Blood",
            "Homocysteine": "Blood",
            
            # Infectious Disease
            "HIV Antibody Test": "Blood",
            "Hepatitis Panel": "Blood",
            "Rapid Strep Test": "Throat Swab",
            "Influenza Test": "Nasal Swab",
            "COVID-19 PCR Test": "Nasal Swab",
            "Blood Culture": "Blood",
            
            # Hormone Tests
            "TSH (Thyroid Stimulating Hormone)": "Blood",
            "Free T4": "Blood",
            "Testosterone": "Blood",
            "Estrogen": "Blood",
            "Cortisol": "Blood",
            
            # Tumor Markers
            "PSA (Prostate-Specific Antigen)": "Blood",
            "CA-125": "Blood",
            "CEA (Carcinoembryonic Antigen)": "Blood",
            "AFP (Alpha-Fetoprotein)": "Blood",
            
            # Other Common Tests
            "Vitamin D Level": "Blood",
            "Vitamin B12 Level": "Blood",
            "Iron Studies": "Blood",
            "Ferritin Level": "Blood",
            "CRP (C-Reactive Protein)": "Blood",
            "ESR (Erythrocyte Sedimentation Rate)": "Blood",
            
            # Microbiology
            "Gram Stain": "Varies",
            "AFB Smear and Culture": "Sputum",
            "Fungal Culture": "Varies",
            "Ova and Parasite Exam": "Stool",
            
            # Therapeutic Drug Monitoring
            "Digoxin Level": "Blood",
            "Lithium Level": "Blood",
            "Vancomycin Trough": "Blood",
            
            # Toxicology
            "Blood Alcohol Level": "Blood",
            "Comprehensive Drug Screen": "Urine/Blood",
            "Heavy Metal Panel": "Blood/Urine",
        }
        
        return self.random_element(list(lab_tests.keys()))

    def insurance_number(self):
        # Example: 9-digit numbers, can be customized
        import random
        return f"{random.randint(100000000, 999999999)}"

    def patient_id(self):
        # Example: PID followed by 6 digits
        import random
        return f"PID{random.randint(100000, 999999)}"

    def gender(self):
        # You can customize this list as needed
        return self.random_element(["male", "female", "non-binary", "other"])
    
    def person(self):
        # Use Faker's built-in name generation for realistic names
        return self.generator.name()

    def email_address(self):
        return self.generator.email()

    def credit_card(self):
        return self.generator.credit_card_number()
        #return self.random_element(["4203895020367512", "4454794511390933", "4203895020367512", "4203895020367512"])

    def us_ssn(self):
        return self.generator.ssn()
        #return self.random_element(["123-45-6789", "987-65-4321", "111-11-1111", "222-22-2222"])
    def url(self):
        """Generate a random URL with realistic structure."""
        import random
        import string
    
        # Common TLDs
        tlds = ['.com', '.org', '.net', '.io', '.co', '.ai', '.dev', '.app', '.tech']
    
        # Common URL paths
        paths = [
            '',  # No path
            '/blog',
            '/articles',
            '/products',
            '/about',
            '/contact',
            '/pricing',
            '/docs',
            '/download',
            '/account'
        ]
    
        # Common query parameters
        params = [
            '',
            '?ref=random',
            '?source=google',
            '?utm_source=newsletter',
            '?id={}'.format(random.randint(1000, 9999)),
            '?page={}'.format(random.randint(1, 10))
        ]
    
        # Generate random domain name
        domain_length = random.randint(5, 12)
        domain = ''.join(random.choices(string.ascii_lowercase, k=domain_length))
    
        # Build the URL
        url_parts = [
            'https://www.' if random.random() > 0.3 else 'http://',  # 70% chance of https
            domain,
            random.choice(tlds),
            random.choice(paths),
            random.choice(params)
        ]
    
        # Randomly add a subdomain
        if random.random() > 0.7:  # 30% chance of having a subdomain
            subdomain = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
            url_parts.insert(1, f"{subdomain}.")
    
        return ''.join(url_parts)

    def location(self):
        """Generate a realistic location string in various formats."""
        import random
        from faker.providers.address.en_US import Provider as AddressProvider
        
        # Common location formats
        formats = [
            # City, State
            "{city}, {state_abbr}",
            "{city}, {state}",
            # Full address
            "{street_address}, {city}, {state_abbr} {zipcode}",
            # Hospital/Clinic names
            #"{hospital_name} {location_type}",
            # Generic location
            #"{location_type} in {city}, {state_abbr}",
            # Just city
            "{city}",
            # Neighborhood
            #"{neighborhood} {location_type}, {city}",
        ]
        
        # Location types (hospitals, clinics, etc.)
        location_types = [
            "Hospital", "Medical Center", "Clinic", "Health Center",
            "Urgent Care", "Medical Office", "Surgery Center", "ER",
            "Pediatric Center", "Women's Health Center"
        ]
        
        # Neighborhood names (can be expanded)
        neighborhoods = [
            "Downtown", "Uptown", "Westside", "East End", "North Hills",
            "South Park", "Riverside", "Highland", "Oakwood", "Pinecrest",
            "Lakeview", "Cedar Grove", "Maplewood", "Hillside", "Valley"
        ]
        
        # Get Faker's address provider
        fake = self.generator
        #address = AddressProvider(fake)
        
        # Generate location components
        city = fake.city()
        state = fake.state()
        state_abbr = fake.state_abbr(include_territories=True)
        street_address = fake.street_address()
        zipcode = fake.zipcode()
        #hospital_name = fake.last_name() + " " + random.choice(location_types)
        #location_type = random.choice(location_types).lower()
        #neighborhood = random.choice(neighborhoods)
        
        # Format the location string
        location_format = random.choice(formats)
        location = location_format.format(
            city=city,
            state=state,
            state_abbr=state_abbr,
            street_address=street_address,
            zipcode=zipcode,
            #hospital_name=hospital_name,
            #location_type=location_type,
            #neighborhood=neighborhood
        )
        
        # Sometimes add country (20% chance)
        if random.random() < 0.2:
            location += f", {fake.country()}"
        
        # Sometimes add directions or landmarks (15% chance)
        """  if random.random() < 0.15:
            landmarks = [
                "across from the mall",
                "next to the park",
                "near the highway",
                "behind the shopping center",
                "in the medical district",
                "downtown",
                "in the city center"
            ]
            location += f" ({random.choice(landmarks)})" """
        
        return location

class OrganizationProviderNew(BaseProvider):
    """Custom provider for generating organization names across various industries."""
    
    def organization(self) -> str:
        """Generate a random organization name."""
        formats = [
            # Standard formats
            "{prefix} {industry}",
            "{industry} {suffix}",
            "{prefix} {industry} {suffix}",
            #"{industry} of {location}",
            #"The {industry} of {location}",
            "{industry} {location}",
            # Tech company formats
            "{prefix} {tech_term} {suffix}",
            "{prefix} {tech_term}",
            "{tech_term} {suffix}",
            # Financial formats
            "{prefix} {financial_term}",
            "{financial_term} {suffix}",
            # Healthcare formats
            "{prefix} {health_term}",
            "{health_term} {suffix}",
            # Educational formats
            #"{location} {education_term}",
            "{prefix} {education_term}",
            # Government formats
            #"{location} {government_term}",
            "{government_term} of {location}",
        ]
        
        # Organization parts
        prefixes = [
            "Global", "National", "International", "United", "First", "Advanced",
            "Elite", "Premier", "Summit", "Peak", "Apex", "Zenith", "Nexus",
            "Pinnacle", "Vertex", "Crest", "Crown", "Empire", "Dynasty", "Horizon",
            "Quantum", "Nova", "Vega", "Orion", "Aurora", "Titan", "Aegis", "Vanguard",
            "Sentinel", "Pinnacle", "Summit", "Crest", "Apex", "Zenith", "Nexus"
        ]
        
        industries = [
            "Solutions", "Systems", "Technologies", "Enterprises", "Holdings",
            "Ventures", "Group", "Partners", "Associates", "Services", "Industries",
            "Corporation", "Inc", "LLC", "Ltd", "Co", "and Co", "and Sons", "and Daughters"
        ]
        
        suffixes = [
            "International", "Global", "Worldwide", "Technologies", "Solutions",
            "Systems", "Enterprises", "Holdings", "Ventures", "Group", "Partners",
            "Associates", "Consulting", "Services", "Industries", "Corporation",
            "Incorporated", "Limited", "LLC", "Ltd", "Co", "and Co"
        ]
        
        tech_terms = [
            "Tech", "Digital", "Cloud", "Data", "Info", "Cyber", "Nano", "Quantum",
            "Synergy", "Nexus", "Matrix", "Vortex", "Pulse", "Nebula", "Orbit",
            "Vortex", "Pulse", "Nebula", "Orbit", "Vortex", "Pulse", "Nebula", "Orbit"
        ]
        
        financial_terms = [
            "Capital", "Wealth", "Trust", "Financial", "Invest", "Asset", "Equity",
            "Venture", "Capital", "Wealth", "Trust", "Financial", "Invest", "Asset",
            "Equity", "Venture", "Capital", "Wealth", "Trust", "Financial", "Invest"
        ]
        
        health_terms = [
            "Health", "Medical", "Care", "Wellness", "Life", "Vital", "Cure",
            "Heal", "Therapy", "Med", "Pharma", "Bio", "Gen", "Vita", "Nova",
            "Apex", "Summit", "Peak", "Pinnacle", "Zenith", "Nexus", "Aurora"
        ]
        
        education_terms = [
            "University", "College", "Institute", "Academy", "School", "Center",
            "Conservatory", "Seminary", "Polytechnic", "Conservatoire", "Lyceum",
            "Gymnasium", "Institution", "Consortium", "Foundation", "Alliance"
        ]
        
        government_terms = [
            "Government", "Administration", "Bureau", "Agency", "Department",
            "Ministry", "Office", "Commission", "Authority", "Service", "Board",
            "Council", "Chamber", "Federation", "Union", "Alliance", "League",
            "Confederation", "Directorate", "Secretariat"
        ]
        
        # Additional data
        locations = [
            "New York", "London", "Tokyo", "Singapore", "Zurich", "Hong Kong",
            "Silicon Valley", "Boston", "Seattle", "Austin", "Berlin", "Paris",
            "Mumbai", "Shanghai", "Sydney", "Toronto", "Dubai", "Amsterdam"
        ]
        
        # Choose a random format and fill in the placeholders
        format_str = self.random_element(formats)
        
        return format_str.format(
            prefix=self.random_element(prefixes),
            industry=self.random_element(industries),
            suffix=self.random_element(suffixes),
            tech_term=self.random_element(tech_terms),
            financial_term=self.random_element(financial_terms),
            health_term=self.random_element(health_terms),
            education_term=self.random_element(education_terms),
            government_term=self.random_element(government_terms),
            location=self.random_element(locations)
        )

class UsPassportProvider(BaseProvider):
    """Provider for US passport numbers and related information."""
    
    def __init__(self, generator):
        super().__init__(generator=generator)
        # Passport book number format: 1-2 letters followed by 6-9 digits
        # Example: C12345678, AB1234567
        self.passport_book_number_formats = (
            '?########',  # 1 letter + 8 digits
            '?#######',   # 1 letter + 7 digits
            '??#######',  # 2 letters + 7 digits
            '??########', # 2 letters + 8 digits
            '?#########'  # 1 letter + 9 digits
        )
        
    def us_passport_number(self) -> str:
        """Generate a random US passport number.
        
        US passport numbers are typically 6-9 alphanumeric characters.
        The first character is always a letter (C, F, G, H, J, K, etc.),
        followed by 5-8 digits.
        """
        # First character is a letter (excluding I, O, Q, S for readability)
        first_char = self.random_letter().upper()
        while first_char in 'IOQS':
            first_char = self.random_letter().upper()
            
        # Remaining characters are digits
        length = self.random_int(6, 9) - 1  # -1 because we already have the first char
        number = ''.join([str(self.random_digit()) for _ in range(length)])
        
        return f"{first_char}{number}"
    
    def us_passport(self) -> str:
        """Generate a random US passport number.
        
        US passport numbers are typically 6-9 alphanumeric characters.
        The first character is always a letter (C, F, G, H, J, K, etc.),
        followed by 5-8 digits.
        """
        # First character is a letter (excluding I, O, Q, S for readability)
        first_char = self.random_letter().upper()
        while first_char in 'IOQS':
            first_char = self.random_letter().upper()
            
        # Remaining characters are digits
        length = self.random_int(6, 9) - 1  # -1 because we already have the first char
        number = ''.join([str(self.random_digit()) for _ in range(length)])
        
        return f"{first_char}{number}"

    def passport_book_number(self) -> str:
        """Generate a passport book number (not the same as passport number).
        
        Format: 1-2 letters followed by 6-9 digits.
        Example: C12345678, AB1234567
        """
        return self.bothify(text=self.random_element(self.passport_book_number_formats)).upper()

    def bank_number(self):
        """Generate a US bank account number.
        
        Args:
            length: Optional length of account number (typically 8-17 digits)
                   If not provided, will use a random length between 8-12 digits.
        """
        length = self.random_int(10, 12)
        return str(self.random_number(digits=length, fix_len=True))

    def iban_code(self):
        """Generate a valid IBAN (International Bank Account Number).
        
        Returns:
            str: A valid IBAN number.
        """
        # Country code to IBAN format mapping (format: CC00BBBBBBBBBBBBBBBB where B=alphanumeric)
        iban_formats = {
            'US': 'US2!n6a8n',  # Not standard, just for example
            'GB': 'GB29!n4a6n8n',
            'DE': 'DE89!n8n10n',
            'FR': 'FR14!n5n5n11n2n',
            'IT': 'IT60!na1!n5n5n12n',
            'ES': 'ES80!n4n4n1n1n10n',
            'NL': 'NL91!n4a10n',
            'CH': 'CH93!n5n12n',
            'BE': 'BE68!n3n7n2n',
            'AT': 'AT61!n5n11n',
        }
        
        # Select a random country
        country_code = self.random_element(list(iban_formats.keys()))
        format_spec = iban_formats[country_code]
        
        # Extract the BBAN format (after the first 4 characters)
        bban_format = format_spec[4:]
        bban = []
        
        i = 0
        while i < len(bban_format):
            if bban_format[i] == '!':
                # Handle fixed length digits
                if i + 1 < len(bban_format) and bban_format[i+1] == 'n':
                    length = 1
                    if i + 2 < len(bban_format) and bban_format[i+2].isdigit():
                        # Handle multi-digit length
                        length = int(bban_format[i+2])
                        i += 1
                    bban.append(str(self.random_number(digits=length, fix_len=True)))
                    i += 2
                else:
                    i += 1
            elif bban_format[i] == 'n':
                # Handle variable length digits
                bban.append(str(self.random_digit()))
                i += 1
            elif bban_format[i] == 'a':
                # Handle letters
                bban.append(self.random_uppercase_letter())
                i += 1
            else:
                i += 1
        
        bban_str = ''.join(bban)
        
        # Calculate check digits
        check_digits = self._calculate_iban_check_digits(country_code, bban_str)
        
        # Return full IBAN
        return f"{country_code}{check_digits}{bban_str}"

    def _calculate_iban_check_digits(self, country_code: str, bban: str) -> str:
        """Calculate IBAN check digits using the MOD-97-10 algorithm."""
        # Move country code and check digits to end
        temp = f"{bban}{country_code}00"
        
        # Convert letters to numbers (A=10, B=11, ..., Z=35)
        def char_to_num(c):
            return str(10 + ord(c.upper()) - ord('A')) if c.isalpha() else c
        
        # Convert to digits
        digits = ''.join(char_to_num(c) for c in temp)
        
        # Calculate mod 97
        mod = int(digits) % 97
        
        # Check digits are 98 - mod
        check = 98 - mod
        return f"{check:02d}"

    def random_uppercase_letter(self) -> str:
        """Generate a random uppercase letter."""
        return chr(self.random_int(65, 90))  # A-Z

