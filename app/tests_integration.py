from django.shortcuts import reverse
from django.test import TestCase

from app.models import Client, Medicine, Product, Provider, Vet, Pet, Breed, City
import datetime


class HomePageTest(TestCase):
    def test_use_home_template(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")


class ClientsTest(TestCase):

    def test_validation_invalid_name_space(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": " ",
                "phone": "5422165438",
                "city": "Berisso",
                "email": "email@vetsoft.com",
            },
        )
        self.assertContains(response, "El nombre no puede estar vacío o contener solo espacios")
        
    def test_repo_use_repo_template(self):
        response = self.client.get(reverse("clients_repo"))
        self.assertTemplateUsed(response, "clients/repository.html")

    def test_repo_display_all_clients(self):
        response = self.client.get(reverse("clients_repo"))
        self.assertTemplateUsed(response, "clients/repository.html")

    def test_form_use_form_template(self):
        response = self.client.get(reverse("clients_form"))
        self.assertTemplateUsed(response, "clients/form.html")

    def test_can_create_client(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Juan Sebastian Veron",
                "phone": "54221555232",
                "city": City.BERISSO,
                "email": "brujita75@vetsoft.com",
            },
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 1)

        self.assertEqual(clients[0].name, "Juan Sebastian Veron")
        self.assertEqual(clients[0].phone, 54221555232)
        self.assertEqual(clients[0].city, City.BERISSO)
        self.assertEqual(clients[0].email, "brujita75@vetsoft.com")

        self.assertRedirects(response, reverse("clients_repo"))

    def test_validation_errors_create_client(self):
        response = self.client.post(
            reverse("clients_form"),
            data={},
        )

        self.assertContains(response, "El nombre no puede estar vacío o contener solo espacios")
        self.assertContains(response, "Por favor ingrese un teléfono")
        self.assertContains(response, "Por favor ingrese un email")

    def test_should_response_with_404_status_if_client_doesnt_exists(self):
        response = self.client.get(reverse("clients_edit", kwargs={"id": 100}))
        self.assertEqual(response.status_code, 404)

    def test_validation_invalid_email(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Juan Sebastian Veron",
                "phone": "54221555232",
                "email": "brujita75",
                "address": "13 y 44",
            },
        )

        self.assertContains(response, "El email debe contener @")

    def test_validation_invalid_name(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "1234$#%",
                "phone": "22165438",
                "address": "1 y 62",
                "email": "tomasbret@hotmail.com",
            },
        )
        self.assertContains(
            response, "El nombre solo puede contener letras y espacios")

    def test_validation_errors_create_client_with_invalid_email_domain(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Juan Perez",
                "phone": "123456789",
                "address": "Calle Falsa 123",
                "email": "juan@gmail.com",
            },
        )

        self.assertContains(
            response, "Por favor el email debe ser del dominio @vetsoft.com")

    def test_can_create_a_client_city(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Nombre",
                "phone": "54312321",
                "city": City.BERISSO,
                "email": "email@vetsoft.com",
            },
        )

        clients = Client.objects.all()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0].name, "Nombre")
        self.assertEqual(clients[0].phone, 54312321)
        self.assertEqual(clients[0].email, "email@vetsoft.com")
        self.assertEqual(clients[0].city, City.BERISSO)

    def test_cannot_create_a_client_city(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Nombre",
                "phone": "54312321",
                "city": "Ciudad",
                "email": "email@vetsoft.com",
            },
        )

        clients = Client.objects.all()
        self.assertEqual(len(clients), 0)
        self.assertContains(response, "Por favor ingrese una ciudad")


class MedicinesTest(TestCase):
    def test_can_create_medicine(self):
        response = self.client.post(
            reverse("medicines_form"),
            data={
                "name": "Amoxicilina",
                "description": "Antibiotico de amplio espectro",
                "dose": "6",
            },
        )
        medicines = Medicine.objects.all()
        self.assertEqual(len(medicines), 1)

        self.assertEqual(medicines[0].name, "Amoxicilina")
        self.assertEqual(medicines[0].description,
                         "Antibiotico de amplio espectro")
        self.assertEqual(medicines[0].dose, 6)

        self.assertRedirects(response, reverse("medicines_repo"))

    def test_update_medicine_with_invalid_dose_zero(self):
        response = self.client.post(
            reverse("medicines_form"),
            data={
                "name": "Amoxicilina",
                "description": "Antibiotico de amplio espectro",
                "dose": "0",
            },
        )
        self.assertContains(response, "La dosis debe estar entre 1 a 10")

    def test_update_medicine_with_invalide_dose(self):
        response = self.client.post(
            reverse("medicines_form"),
            data={
                "name": "Amoxicilina",
                "description": "Antibiotico de amplio espectro",
                "dose": "11",
            },
        )
        self.assertContains(response, "La dosis debe estar entre 1 a 10")

    def test_update_medicine_with_invalid_dose_negative(self):
        response = self.client.post(
            reverse("medicines_form"),
            data={
                "name": "Amoxicilina",
                "description": "Antibiotico de amplio espectro",
                "dose": "-5",
            },
        )
        self.assertContains(
            response, "La dosis debe ser un número entero positivo")


class ProviderTest(TestCase):
    def test_can_create_provider_with_address(self):
        response = self.client.post(
            reverse("providers_form"),
            data={
                "name": "Pepe Gonzales",
                "email": "pepe@hotmail.com",
                "address": "7 entre 13 y 44",
            },
        )
        provider = Provider.objects.first()

        self.assertEqual(provider.name, "Pepe Gonzales")
        self.assertEqual(provider.email, "pepe@hotmail.com")
        self.assertEqual(provider.address, "7 entre 13 y 44")

        self.assertRedirects(response, reverse("providers_repo"))

    def test_validation_errors_create_provider_without_address(self):
        response = self.client.post(
            reverse("providers_form"),
            data={
                "name": "Pepe Gonzales",
                "email": "pepe@hotmail.com",
                # No se proporciona la dirección
            },
        )

        self.assertContains(response, "Por favor ingrese una dirección")


class VetsTest(TestCase):
    def test_can_create_vet(self):
        response = self.client.post(
            reverse("vets_form"),
            data={
                "name": "Joaquin Munos",
                "phone": "22165438",
                "address": "20 y 60",
                "email": "joaquin10@hotmail.com",
                "especialidad": "general",
            },
        )
        vets = Vet.objects.all()
        self.assertEqual(len(vets), 1)

        self.assertEqual(vets[0].name, "Joaquin Munos")
        self.assertEqual(vets[0].phone, "22165438")
        self.assertEqual(vets[0].address, "20 y 60")
        self.assertEqual(vets[0].email, "joaquin10@hotmail.com")
        self.assertEqual(vets[0].speciality, "general")

        self.assertRedirects(response, reverse("vets_repo"))

    def test_validation_invalid_especialidad(self):
        response = self.client.post(
            reverse("vets_form"),
            data={
                "name": "Joaquin Munos",
                "phone": "22165438",
                "address": "20 y 60",
                "email": "joaquin10@hotmail.com",
                "especialidad": "",
            },
        )

        self.assertContains(
            response, "Por favor seleccione una especialidad")


class ProductsTest(TestCase):
    def test_can_create_product(self):
        response = self.client.post(
            reverse("products_form"),
            data={
                "name": "NombreProducto",
                "type": "TipoProducto",
                "price": 8,
            },
        )
        products = Product.objects.all()
        self.assertEqual(len(products), 1)

        self.assertEqual(products[0].name, "NombreProducto")
        self.assertEqual(products[0].type, "TipoProducto")
        self.assertEqual(products[0].price, 8)

        self.assertRedirects(response, reverse("products_repo"))

    def test_create_product_negative_product(self):
        response = self.client.post(
            reverse("products_form"),
            data={
                "name": "NombreProducto",
                "type": "TipoProducto",
                "price": -8,
            },
        )
        self.assertContains(response, "El precio debe ser mayor a cero")

    def test_create_product_no_product(self):
        response = self.client.post(
            reverse("products_form"),
            data={
                "name": "NombreProducto",
                "type": "TipoProducto",
                "price": 0,
            },
        )
        self.assertContains(response, "El precio debe ser mayor a cero")


class ClientsTestPhone(TestCase):
    def test_can_create_client_phone_54(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Nombre",
                "phone": "54221555232",
                "city": City.BERISSO,
                "email": "email@vetsoft.com",
            },
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 1)

        self.assertEqual(clients[0].name, "Nombre")
        self.assertEqual(clients[0].phone, 54221555232)
        self.assertEqual(clients[0].city, City.BERISSO)
        self.assertEqual(clients[0].email, "email@vetsoft.com")

        self.assertRedirects(response, reverse("clients_repo"))

    def test_cannot_create_client_phone(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Nombre",
                "phone": "221555232",
                "address": "Direccion",
                "email": "email@vetsoft.com",
            },
        )
        self.assertContains(response, "El teléfono debe comenzar con 54")


class PetTest(TestCase):
    def test_can_create_pet(self):
        response = self.client.post(
            reverse("pets_form"),
            data={
                "name": "Nombre",
                "breed": "Dog",
                "birthday": "2024-06-01",
            },

        )
        pets = Pet.objects.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].name, "Nombre")
        self.assertEqual(pets[0].breed, Breed.DOG)
        self.assertEqual(pets[0].birthday, datetime.date(2024, 6, 1))

    def test_cannot_create_pet(self):
        response = self.client.post(
            reverse("pets_form"),
            data={
                "name": "Nombre",
                "breed": "Mascota",
                "birthday": "2024-06-01",
            },
        )
        pets = Pet.objects.all()
        self.assertEqual(len(pets), 0)
        self.assertContains(response, "No esta esa opcion")

    def test_breed_choices(self):
        # Crea mascotas con cada opción de raza usando la función save_pet
        response_dog = self.client.post(
            reverse("pets_form"),
            data={
                "name": "Dog Pet",
                "breed": Breed.DOG,
                "birthday": "2022-01-01",
            }
        )
        response_cat = self.client.post(
            reverse("pets_form"),
            data={
                "name": "Cat Pet",
                "breed": Breed.CAT,
                "birthday": "2022-01-01",
            }
        )
        response_bird = self.client.post(
            reverse("pets_form"),
            data={
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
