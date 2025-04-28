from django.test import TestCase

from app.models import Breed, Client, Medicine, Pet, Product, Provider, Vet, City
import datetime


class ProviderModelTest(TestCase):
    def test_update_provider_address_with_error(self):
        Provider.save_provider(
            {
                "name": "Pepe Gonzales",
                "email": "pepe@hotmail.com",
                "address": "7 entre 13 y 44",
            }
        )
        provider = Provider.objects.get(pk=1)

        self.assertEqual(provider.address, "7 entre 13 y 44")

        # Intentar actualizar la dirección con un valor inválido (cadena vacía)
        success, errors = provider.update_provider({"address": ""})

        # Verificar que la actualización no fue exitosa
        self.assertFalse(success)

        # Verificar que se generaron errores
        self.assertIsNotNone(errors)


class ClientModelTest(TestCase):

    def test_can_create_and_get_client_space(self):
        response = Client.save_client(
            {
                "name": " ",
                "phone": "54221555232",
                "city": City.BERISSO,
                "email": "email@vetsoft.com",
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 0)
        self.assertEqual(response[1]["name"], "El nombre no puede estar vacío o contener solo espacios")
    
    def test_can_create_a_client_city(self):
        response = Client.save_client(
            {
                "name": "Nombre",
                "phone": "54666777",
                "email": "email@vetsoft.com",
                "city": City.BERISSO,
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 1)

        self.assertEqual(clients[0].name, "Nombre")
        self.assertEqual(clients[0].phone, 54666777)
        self.assertEqual(clients[0].email, "email@vetsoft.com")
        self.assertEqual(clients[0].city, City.BERISSO)

    def test_cannot_create_a_client_city(self):
        response = Client.save_client(
            {
                "name": "Nombre",
                "phone": "54666777",
                "email": "email@vetsoft.com",
                "city": "Ciudad",
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 1)
        self.assertEqual(response[1]["city"],
                         "Por favor ingrese una ciudad válida")

    def test_phone_empty(self):
        response = Client.save_client(
            {
                "name": "Juan Sebastian Veron",
                "phone": "",
                "address": "13 y 44",
                "email": "brujita75@hotmail.com",
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 0)
        self.assertEqual(response[1]['phone'], 'Por favor ingrese un teléfono')

    def test_phone_not_numeric(self):
        response = Client.save_client(
            {
                "name": "Juan Sebastian Veron",
                "phone": "123abc",
                "address": "13 y 44",
                "email": "brujita75@hotmail.com",
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 0)
        self.assertEqual(response[1]['phone'],
                         'Por favor ingrese un teléfono ')
        print(response[1]["phone"])

    def test_phone_zero(self):
        response = Client.save_client(
            {
                "name": "Juan Sebastian Veron",
                "phone": "0",
                "address": "13 y 44",
                "email": "brujita75@vetsoft.com",
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 0)
        self.assertEqual(response[1]['phone'], 'El número debe ser positivo')

    def test_email_empty_local_part(self):
        success, errors = Client.save_client(
            {
                "name": "Juan Perez",
                "phone": "123456789",
                "address": "Calle Falsa 123",
                "email": "@vetsoft.com",
            }
        )
        self.assertFalse(success)
        self.assertIn("email", errors)
        self.assertEqual(
            errors["email"], "Por favor el email debe tener una parte local antes de @vetsoft.com")

    def test_can_update_client(self):
        Client.save_client(
            {
                "name": "Juan Sebastian Veron",
                "phone": "54221555232",
                "address": "13 y 44",
                "email": "brujita75@vetsoft.com",
            }
        )
        client = Client.objects.get(pk=1)

        self.assertEqual(client.phone, "54221555232")

        client.update_client({"phone": "54221555233"})

        client_updated = Client.objects.get(pk=1)

        self.assertEqual(client_updated.phone, "54221555233")


class ClientModelTest(TestCase):
    def test_can_create_and_get_client(self):
        response = Client.save_client(
            {
                "name": "234#~$",
                "phone": "221555232",
                "address": "13 y 44",
                "email": "brujita75@hotmail.com",
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 0)
        self.assertEqual(
            response[1]["name"], "El nombre solo puede contener letras y espacios")


class MedicineModelTest(TestCase):
    def test_can_create_and_get_medicine(self):
        success, errors = Medicine.save_medicine(
            {
                "name": "Amoxicilina",
                "description": "Antibiotico de amplio espectro",
                "dose": "6",
            }
        )
        self.assertTrue(success)
        self.assertIsNone(errors)

        medicines = Medicine.objects.all()
        self.assertEqual(len(medicines), 1)

        self.assertEqual(medicines[0].name, "Amoxicilina")
        self.assertEqual(medicines[0].description,
                         "Antibiotico de amplio espectro")
        self.assertEqual(medicines[0].dose, 6)

    def test_update_medicine_with_invalid_dose_zero(self):
        Medicine.save_medicine(
            {
                "name": "Amoxicilina",
                "description": "Antibiotico de amplio espectro",
                "dose": "0",
            }
        )
        medicinas = Medicine.objects.all()
        self.assertEqual(len(medicinas), 0)

    def test_update_medicine_with_invalide_dose(self):
        response = Medicine.save_medicine(
            {
                "name": "Amoxicilina",
                "description": "Antibiotico de amplio espectro",
                "dose": "11",
            }
        )
        medicinas = Medicine.objects.all()
        self.assertEqual(len(medicinas), 0)
        self.assertEqual(response[1]['dose'],
                         'La dosis debe estar entre 1 a 10')

    def test_update_medicine_with_invalid_dose_negative(self):
        response = Medicine.save_medicine(
            {
                "name": "Amoxicilina",
                "description": "Antibiotico de amplio espectro",
                "dose": "-5",
            }
        )
        medicinas = Medicine.objects.all()
        self.assertEqual(len(medicinas), 0)
        self.assertEqual(response[1]['dose'],
                         'La dosis debe ser un número entero positivo')


# Test de veterinario
class VetModelTest(TestCase):
    def test_can_create_and_get_vet(self):
        Vet.save_vet(
            {
                "name": "Tomas Sbert",
                "phone": "2314557290",
                "address": "La Plata 43",
                "email": "tomasbret_dx@hotmail.com",
                "especialidad": "general",
            }
        )

        vets = Vet.objects.all()

        self.assertEqual(len(vets), 1)

        self.assertEqual(vets[0].name, "Tomas Sbert")
        self.assertEqual(vets[0].phone, "2314557290")
        self.assertEqual(vets[0].address, "La Plata 43")
        self.assertEqual(vets[0].email, "tomasbret_dx@hotmail.com")
        self.assertEqual(vets[0].speciality, "general")

    def test_can_delete_vet(self):
        vet = Vet.objects.create(
            name="Tomas Sbert",
            phone="2314557290",
            address="La Plata 43",
            email="tomasbret_dx@hotmail.com",
            speciality="general"
        )

        # Eliminar el veterinario
        vet.delete()

        # Verificar que el veterinario haya sido eliminado
        vets = Vet.objects.all()
        self.assertEqual(len(vets), 0)

        
    def test_can_create_and_get_speciality(self):
        response = Vet.save_vet(
            {
                "name": "234#~$",
                "phone": "221555232",
                "address": "13 y 44",
                "email": "brujita75@hotmail.com",
                "especialidad":"",
            }
        )

        vets = Vet.objects.all()
        self.assertEqual(len(vets),0)
        self.assertEqual(response[1]["especialidad"],"Por favor seleccione una especialidad")

class ProductModelTest(TestCase):
    def test_can_create_and_get_product(self):
        Product.save_product(
            {
                "name": "NombreProducto",
                "type": "TipoProducto",
                "price": 8,
            }
        )

        products = Product.objects.all()
        self.assertEqual(len(products), 1)

        self.assertEqual(products[0].name, "NombreProducto")
        self.assertEqual(products[0].type, "TipoProducto")
        self.assertEqual(products[0].price, 8)

    def test_create_product_with_negative_product(self):
        response = Product.save_product(
            {
                "name": "NombreProducto",
                "type": "TipoProducto",
                "price": -8,
            }
        )

        products = Product.objects.all()
        self.assertEqual(len(products), 0)
        self.assertEqual(response[1]["price"],
                         "El precio debe ser mayor a cero")

    def test_create_product_with_no_product(self):
        response = Product.save_product(
            {
                "name": "NombreProducto",
                "type": "TipoProducto",
                "price": 0,
            }
        )

        products = Product.objects.all()
        self.assertEqual(len(products), 0)
        self.assertEqual(response[1]["price"],
                         "El precio debe ser mayor a cero")


# Agrego test unitarios para punto 5 actividad 3
class PetModelTest(TestCase):
    def test_can_create_a_pet(self):
        response = Pet.save_pet(
            {
                "name": "Nombre",
                "breed": Breed.DOG,
                "birthday": "2024-06-01",
            }
        )

        pets = Pet.objects.all()
        self.assertEqual(len(pets), 1)

        self.assertEqual(pets[0].name, "Nombre")
        self.assertEqual(pets[0].breed, Breed.DOG)
        self.assertEqual(pets[0].birthday, datetime.date(2024, 6, 1))

    def test_breed_choices(self):
        # Crea mascotas con cada opción de raza usando la función save_pet
        response_dog = Pet.save_pet(
            {
                "name": "Dog Pet",
                "breed": Breed.DOG,
                "birthday": "2022-01-01",
            }
        )
        response_cat = Pet.save_pet(
            {
                "name": "Cat Pet",
                "breed": Breed.CAT,
                "birthday": "2022-01-01",
            }
        )
        response_bird = Pet.save_pet(
            {
                "name": "Bird Pet",
                "breed": Breed.BIRD,
                "birthday": "2022-01-01",
            }
        )

        # Verifica que las mascotas se hayan guardado con las razas correctas
        pets = Pet.objects.all()
        self.assertEqual(len(pets), 3)

        self.assertEqual(pets[0].name, "Dog Pet")
        self.assertEqual(pets[0].breed, Breed.DOG)
        self.assertEqual(pets[0].birthday, datetime.date(2022, 1, 1))

        self.assertEqual(pets[1].name, "Cat Pet")
        self.assertEqual(pets[1].breed, Breed.CAT)
        self.assertEqual(pets[1].birthday, datetime.date(2022, 1, 1))

        self.assertEqual(pets[2].name, "Bird Pet")
        self.assertEqual(pets[2].breed, Breed.BIRD)
        self.assertEqual(pets[2].birthday, datetime.date(2022, 1, 1))

    def test_cannot_create_a_pet(self):
        response = Pet.save_pet(
            {
                "name ": "Nombre",
                "breed": "mascota",
                "birthday": "2024-06-01",
            }
        )
        pets = Pet.objects.all()
        self.assertEqual(len(pets), 0)
        self.assertEqual(response[1]["breed"], "No esta esa opcion")


class ClientModelTest(TestCase):
    def test_can_create_client_phone_54(self):
        Client.save_client(
            {
                "name": "Nombre",
                "phone": "541555232",
                "city": "Berisso",
                "email": "hola@vetsoft.com",
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 1)

        self.assertEqual(clients[0].name, "Nombre")
        self.assertEqual(clients[0].phone, 541555232)
        self.assertEqual(clients[0].city, "Berisso")
        self.assertEqual(clients[0].email, "hola@vetsoft.com")

    def test_cannot_create_a_client_phone(self):
        response = Client.save_client(
            {
                "name": "Nombre",
                "phone": "861555232",
                "address": "direccion",
                "email": "hola@vetsoft.com",
            }
        )

        clients = Client.objects.all()
        self.assertEqual(len(clients), 0)
        self.assertEqual(response[1]["phone"],
                         "El teléfono debe comenzar con 54")
