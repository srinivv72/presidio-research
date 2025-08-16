from faker import Faker

from presidio_evaluator.data_generator.faker_extensions import (
    NationalityProvider,
    OrganizationProvider,
    HospitalProvider,
    MedicalProvider,
    UsPassportProvider,
)


def test_nationality_provider():
    faker = Faker()
    faker.add_provider(NationalityProvider)
    element = faker.nation_man()
    assert element


def test_organization_provider():
    faker = Faker()
    faker.add_provider(OrganizationProvider)
    element = faker.organization()
    assert element


def test_hospital_provider():
    faker = Faker()
    faker.add_provider(HospitalProvider)
    element = faker.hospital_name()
    assert element

def test_medical_provider():
    faker = Faker()
    faker.add_provider(MedicalProvider)
    element = faker.drug()
    assert element

def test_us_passport_provider():
    faker = Faker()
    faker.add_provider(UsPassportProvider)
    element = faker.us_passport_number()
    assert element
