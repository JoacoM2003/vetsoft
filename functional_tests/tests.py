import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import Browser, expect, sync_playwright
from app.models import Provider, Vet, Client, City
from playwright.sync_api import Browser, expect, sync_playwright, Playwright
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


class PlaywrightTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright: Playwright = sync_playwright().start()
        cls.browser: Browser = cls.playwright.firefox.launch(
            headless=os.environ.get("HEADLESS", "1") == "1",
            slow_mo=int(os.environ.get("SLOW_MO", "0")),
            args=["--no-sandbox"]  # Importante en CI
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.page = self.browser.new_page()

    def tearDown(self):
        self.page.close()
        super().tearDown()


class HomeTestCase(PlaywrightTestCase):
    def test_should_have_navbar_with_links(self):
        self.page.goto(self.live_server_url)

        navbar_home_link = self.page.get_by_test_id("navbar-Home")

        expect(navbar_home_link).to_be_visible()
        expect(navbar_home_link).to_have_text("Home")
        expect(navbar_home_link).to_have_attribute("href", reverse("home"))

        navbar_clients_link = self.page.get_by_test_id("navbar-Clientes")

        expect(navbar_clients_link).to_be_visible()
        expect(navbar_clients_link).to_have_text("Clientes")
        expect(navbar_clients_link).to_have_attribute(
            "href", reverse("clients_repo"))

    def test_should_have_home_cards_with_links(self):
        self.page.goto(self.live_server_url)

        home_clients_link = self.page.get_by_test_id("home-Clientes")

        expect(home_clients_link).to_be_visible()
        expect(home_clients_link).to_have_text("Clientes")
        expect(home_clients_link).to_have_attribute(
            "href", reverse("clients_repo"))


class ProvidersRepoTestCase(PlaywrightTestCase):

    def test_should_show_provider_address(self):
        Provider.objects.create(
            name="Carlos Perez",
            email="carlos@example.com",
            address="Calle falsa 123",
        )
        self.page.goto(f"{self.live_server_url}{reverse('providers_repo')}")

        expect(self.page.get_by_text("Calle falsa 123")).to_be_visible()

    def test_should_require_address_on_provider_form(self):
        self.page.goto(f"{self.live_server_url}{reverse('providers_form')}")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese una dirección")).to_be_visible()

    def test_should_show_error_for_invalid_email_domain(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        self.page.get_by_label("Nombre").fill("Juan Pérez")
        self.page.get_by_label("Teléfono").fill("123456789")
        self.page.get_by_label("Email").fill("juan@example")
        self.page.get_by_label("Ciudad").select_option(City.BERISSO)

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor el email debe ser del dominio @vetsoft.com")).to_be_visible()


class ClientsRepoTestCase(PlaywrightTestCase):

    def test_should_not_be_able_to_create_a_name_space(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill(" ")
        self.page.get_by_label("Ciudad").select_option("Berisso")
        self.page.get_by_label("Teléfono").fill("5423145553")
        self.page.get_by_label("Email").fill("eduardola@vetsoft.com")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "El nombre no puede estar vacío o contener solo espacios")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un teléfono")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un email")).not_to_be_visible()
        

    def test_should_show_message_if_table_is_empty(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        expect(self.page.get_by_text("No existen clientes")).not_to_be_visible()

        expect(self.page.get_by_text("Juan Sebastián Veron")).to_be_visible()
        expect(self.page.get_by_text("13 y 44")).to_be_visible()
        expect(self.page.get_by_text("221555232")).to_be_visible()
        expect(self.page.get_by_text("brujita75@hotmail.com")).to_be_visible()

        expect(self.page.get_by_text("Guido Carrillo")).to_be_visible()
        expect(self.page.get_by_text("1 y 57")).to_be_visible()
        expect(self.page.get_by_text("221232555")).to_be_visible()
        expect(self.page.get_by_text("goleador@gmail.com")).to_be_visible()

    def test_should_show_add_client_action(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        add_client_action = self.page.get_by_role(
            "link", name="Nuevo cliente", exact=False
        )
        expect(add_client_action).to_have_attribute(
            "href", reverse("clients_form"))

    def test_should_show_client_edit_action(self):
        client = Client.objects.create(
            name="Juan Sebastián Veron",
            city=City.BERISSO,
            phone="54221555232",
            email="brujita75@vetsoft.com",
        )

        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        edit_action = self.page.get_by_role("link", name="Editar")
        expect(edit_action).to_have_attribute(
            "href", reverse("clients_edit", kwargs={"id": client.id})
        )

    def test_should_show_client_delete_action(self):
        client = Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone="221555232",
            email="brujita75@hotmail.com",
        )

        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        edit_form = self.page.get_by_role(
            "form", name="Formulario de eliminación de cliente"
        )
        client_id_input = edit_form.locator("input[name=client_id]")

        expect(edit_form).to_be_visible()
        expect(edit_form).to_have_attribute(
            "action", reverse("clients_delete"))
        expect(client_id_input).not_to_be_visible()
        expect(client_id_input).to_have_value(str(client.id))
        expect(edit_form.get_by_role("button", name="Eliminar")).to_be_visible()

    def test_should_can_be_able_to_delete_a_client(self):
        Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone="221555232",
            email="brujita75@hotmail.com",
        )

        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        expect(self.page.get_by_text("Juan Sebastián Veron")).to_be_visible()

        def is_delete_response(response):
            return response.url.find(reverse("clients_delete"))

        # verificamos que el envio del formulario fue exitoso
        with self.page.expect_response(is_delete_response) as response_info:
            self.page.get_by_role("button", name="Eliminar").click()

        response = response_info.value
        self.assertTrue(response.status < 400)

        expect(self.page.get_by_text("Juan Sebastián Veron")).not_to_be_visible()


class ClientCreateEditTestCase(PlaywrightTestCase):
    def test_should_be_able_to_create_a_new_client(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Juan Sebastian Veron")
        self.page.get_by_label("Teléfono").fill("54221555232")
        self.page.get_by_label("Email").fill("brujita75@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option(City.BERISSO)

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Juan Sebastian Veron")).to_be_visible()
        expect(self.page.get_by_text("54221555232")).to_be_visible()
        expect(self.page.get_by_text("brujita75@vetsoft.com")).to_be_visible()
        expect(self.page.get_by_text(City.BERISSO)).to_be_visible()

    def test_should_view_errors_if_form_is_invalid(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "El nombre no puede estar vacío o contener solo espacios")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un teléfono")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un email")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Juan Sebastián Veron")
        self.page.get_by_label("Teléfono").fill("54221555232")
        self.page.get_by_label("Email").fill("brujita75")
        self.page.get_by_label("Ciudad").select_option("Seleccione una opción")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).not_to_be_visible()
        expect(
            self.page.get_by_text("Por favor ingrese un teléfono")
        ).not_to_be_visible()

        expect(
            self.page.get_by_text("El email debe contener @")
        ).to_be_visible()

    def test_should_be_able_to_edit_a_client(self):
        client = Client.objects.create(
            name="Juan Sebastián Veron",
            city=City.BERISSO,
            phone="54221555232",
            email="brujita75@vetsoft.com",
        )

        path = reverse("clients_edit", kwargs={"id": client.id})
        self.page.goto(f"{self.live_server_url}{path}")

        self.page.get_by_label("Nombre").fill("Guido Carrillo")
        self.page.get_by_label("Teléfono").fill("54221232555")
        self.page.get_by_label("Email").fill("goleador@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option("Ensenada")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Juan Sebastián Veron")).not_to_be_visible()
        expect(self.page.get_by_text(City.BERISSO)).not_to_be_visible()
        expect(self.page.get_by_text("54221555232")).not_to_be_visible()
        expect(self.page.get_by_text("brujita75@vetsoft.com")).not_to_be_visible()

        expect(self.page.get_by_text("Guido Carrillo")).to_be_visible()
        expect(self.page.get_by_text("Ensenada")).to_be_visible()
        expect(self.page.get_by_text("54221232555")).to_be_visible()
        expect(self.page.get_by_text("goleador@vetsoft.com")).to_be_visible()

        edit_action = self.page.get_by_role("link", name="Editar")
        expect(edit_action).to_have_attribute(
            "href", reverse("clients_edit", kwargs={"id": client.id})
        )

    def test_should_not_be_able_to_create_a_new_client_character_phone(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombrePersona")
        self.page.get_by_label("Teléfono").fill("telefono")
        self.page.get_by_label("Email").fill("email@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option("Berisso")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("NombrePersona")).not_to_be_visible()
        expect(self.page.get_by_text("telefono")).not_to_be_visible()
        expect(self.page.get_by_text("Por favor ingrese un teléfono")).to_be_visible()
        expect(self.page.get_by_text("email@vetsoft.com")).not_to_be_visible()
        expect(self.page.get_by_text("Berisso")).not_to_be_visible()


class ClientsRepoTestCase(PlaywrightTestCase):
    def test_should_not_be_able_to_create_a_name(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("1243##$")
        self.page.get_by_label("Ciudad").select_option(City.BERISSO)
        self.page.get_by_label("Teléfono").fill("5423145553")
        self.page.get_by_label("Email").fill("eduardola@vetsoft.com")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "El nombre solo puede contener letras y espacios")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un teléfono")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un email")).not_to_be_visible()


class ProductCreateTestCase(PlaywrightTestCase):
    def test_should_be_able_to_create_a_new_product(self):
        self.page.goto(f"{self.live_server_url}{reverse('products_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreProducto")
        self.page.get_by_label("Tipo").fill("TipoProducto")
        self.page.get_by_label("Precio").fill("8")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("NombreProducto")).to_be_visible()
        expect(self.page.get_by_text("TipoProducto")).to_be_visible()
        expect(self.page.get_by_text("8.0")).to_be_visible()

    def test_should_not_be_able_to_create_a_negative_product(self):
        self.page.goto(f"{self.live_server_url}{reverse('products_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un tipo del producto")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un precio")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreProducto")
        self.page.get_by_label("Tipo").fill("TipoProducto")
        self.page.get_by_label("Precio").fill("-8")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un tipo del producto")).not_to_be_visible()
        expect(self.page.get_by_text(
            "El precio debe ser mayor a cero")).to_be_visible()

    def test_should_not_be_able_to_create_a_no_product(self):
        self.page.goto(f"{self.live_server_url}{reverse('products_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        self.page.get_by_label("Nombre").fill("NombreProducto")
        self.page.get_by_label("Tipo").fill("TipoProducto")
        self.page.get_by_label("Precio").fill("0")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un tipo del producto")).not_to_be_visible()
        expect(self.page.get_by_text(
            "El precio debe ser mayor a cero")).to_be_visible()


# Test de Vet
class VetsRepoTestCase(PlaywrightTestCase):
    def test_should_show_vets_data(self):
        Vet.objects.create(
            name="Dr. Michael Smith",
            address="789 Oak St",
            phone="555123456",
            email="michael@example.com",
            speciality="general"
        )

        Vet.objects.create(
            name="Dr. Emily Johnson",
            address="101 Pine St",
            phone="555987654",
            email="emily@example.com",
            speciality="dentista"
        )

        self.page.goto(f"{self.live_server_url}{reverse('vets_repo')}")

        expect(self.page.get_by_text(
            "No existen veterinarios")).not_to_be_visible()

        expect(self.page.get_by_text("Dr. Michael Smith")).to_be_visible()
        expect(self.page.get_by_text("789 Oak St")).to_be_visible()
        expect(self.page.get_by_text("555123456")).to_be_visible()
        expect(self.page.get_by_text("michael@example.com")).to_be_visible()

        expect(self.page.get_by_text("Dr. Emily Johnson")).to_be_visible()
        expect(self.page.get_by_text("101 Pine St")).to_be_visible()
        expect(self.page.get_by_text("555987654")).to_be_visible()
        expect(self.page.get_by_text("emily@example.com")).to_be_visible()

    def test_should_not_be_able_to_create_a_especialidad_vacio(self):
        self.page.goto(f"{self.live_server_url}{reverse('vets_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Eduardo")
        self.page.get_by_label("Dirección").fill("La Plata")
        self.page.get_by_label("Teléfono").fill("23145553")
        self.page.get_by_label("Email").fill("eduardola@gmail.com")
        self.page.get_by_label("Especialidad").fill("")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un teléfono")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un email")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor seleccione una especialidad")).to_be_visible()

# TEST MASCOTA


class PetCreateTestCase(PlaywrightTestCase):
    def test_should_be_able_to_create_a_new_pet(self):
        self.page.goto(f"{self.live_server_url}{reverse('pets_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreMascota")
        self.page.get_by_label("Raza").select_option("Dog")
        self.page.get_by_label("Fecha de Nacimiento").fill("2024-06-01")

        self.page.get_by_role("button", name="Guardar").click()
        expect(self.page.get_by_text("NombreMascota")).to_be_visible()
        expect(self.page.get_by_text("Dog")).to_be_visible()
        expect(self.page.get_by_text("June 1, 2024")).to_be_visible()

    def test_should_not_be_able_to_create_a_new_pet(self):
        self.page.goto(f"{self.live_server_url}{reverse('pets_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreMascota")
        self.page.get_by_label("Raza").select_option("Seleccione una opción")
        self.page.get_by_label("Fecha de Nacimiento").fill("2024-06-01")

        self.page.get_by_role("button", name="Guardar").click()
        expect(self.page.get_by_text("No esta esa opcion")).to_be_visible()


class MedicineCreateTestCase(PlaywrightTestCase):
    def test_should_be_able_to_create_a_new_medicine(self):
        self.page.goto(f"{self.live_server_url}{reverse('medicines_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Amoxicilina")
        self.page.get_by_label("Descripción").fill(
            "Antibiotico de amplio espectro")
        self.page.get_by_label("Dosis").fill("6")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Amoxicilina")).to_be_visible()
        expect(self.page.get_by_text(
            "Antibiotico de amplio espectro")).to_be_visible()
        expect(self.page.get_by_text("6")).to_be_visible()

    def test_should_view_errors_if_dose_is_zero(self):
        self.page.goto(f"{self.live_server_url}{reverse('medicines_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese una descripción")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese una dosis")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Amoxicilina")
        self.page.get_by_label("Descripción").fill(
            "Antibiotico de amplio espectro")
        self.page.get_by_label("Dosis").fill("0")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese una descripción")).not_to_be_visible()
        expect(self.page.get_by_text(
            "La dosis debe estar entre 1 a 10")).to_be_visible()

    def test_should_view_errors_if_dose_is_out_of_range(self):
        self.page.goto(f"{self.live_server_url}{reverse('medicines_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese una descripción")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese una dosis")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Amoxicilina")
        self.page.get_by_label("Descripción").fill(
            "Antibiotico de amplio espectro")
        self.page.get_by_label("Dosis").fill("11")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese una descripción")).not_to_be_visible()
        expect(self.page.get_by_text(
            "La dosis debe estar entre 1 a 10")).to_be_visible()

    def test_should_view_errors_if_dose_is_negative(self):
        self.page.goto(f"{self.live_server_url}{reverse('medicines_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese una descripción")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese una dosis")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Amoxicilina")
        self.page.get_by_label("Descripción").fill(
            "Antibiotico de amplio espectro")
        self.page.get_by_label("Dosis").fill("-5")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese una descripción")).not_to_be_visible()
        expect(self.page.get_by_text(
            "La dosis debe ser un número entero positivo")).to_be_visible()


class ClientCreateTestCasePhone(PlaywrightTestCase):
    def test_should_be_able_to_create_a_new_client_phone(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombrePersona")
        self.page.get_by_label("Teléfono").fill("54221555232")
        self.page.get_by_label("Email").fill("email@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option(City.BERISSO)

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("NombrePersona")).to_be_visible()
        expect(self.page.get_by_text("54221555232")).to_be_visible()
        expect(self.page.get_by_text("email@vetsoft.com")).to_be_visible()
        expect(self.page.get_by_text(City.BERISSO)).to_be_visible()

    def test_should_not_be_able_to_create_a_client_phone(self):

        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "El nombre no puede estar vacío o contener solo espacios")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un teléfono")).to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un email")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Nombre")
        self.page.get_by_label("Teléfono").fill("221555232")
        self.page.get_by_label("Email").fill("email@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option("Seleccione una opción")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese un nombre")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un teléfono")).not_to_be_visible()
        expect(self.page.get_by_text(
            "Por favor ingrese un email")).not_to_be_visible()
        expect(self.page.get_by_text(
            "El teléfono debe comenzar con 54")).to_be_visible()


class ClientCreateTestCaseCity(PlaywrightTestCase):
    def test_should_be_able_to_create_a_new_client_city(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreCliente")
        self.page.get_by_label("Teléfono").fill("54221555232")
        self.page.get_by_label("Email").fill("email@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option(City.BERISSO)

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "NombreCliente")).to_be_visible()
        expect(self.page.get_by_text(
            "54221555232")).to_be_visible()
        expect(self.page.get_by_text(
            "email@vetsoft.com")).to_be_visible()
        expect(self.page.get_by_text(
            City.BERISSO)).to_be_visible()

    def test_should_be_able_to_create_a_new_client_city(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreCliente")
        self.page.get_by_label("Teléfono").fill("54221555232")
        self.page.get_by_label("Email").fill("email@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option("Seleccione una opción")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "Por favor ingrese una ciudad")).to_be_visible()

    # test pedido 30 de junio
    # agregar un test e2e que pruebe que todas las opciones de la clase enumerativa se pueden seleccionar en el form.
    def test_city_choices(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreCliente")
        self.page.get_by_label("Teléfono").fill("54221555232")
        self.page.get_by_label("Email").fill("email@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option(City.BERISSO)

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "NombreCliente")).to_be_visible()
        expect(self.page.get_by_text(
            "54221555232")).to_be_visible()
        expect(self.page.get_by_text(
            "email@vetsoft.com")).to_be_visible()
        expect(self.page.get_by_text(
            City.BERISSO)).to_be_visible()

        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreClientee")
        self.page.get_by_label("Teléfono").fill("542215552322")
        self.page.get_by_label("Email").fill("email2@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option("La Plata")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "NombreClientee")).to_be_visible()
        expect(self.page.get_by_text(
            "542215552322")).to_be_visible()
        expect(self.page.get_by_text(
            "email2@vetsoft.com")).to_be_visible()
        expect(self.page.get_by_text(
            "La Plata")).to_be_visible()

        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("NombreClienteee")
        self.page.get_by_label("Teléfono").fill("542215552323")
        self.page.get_by_label("Email").fill("email3@vetsoft.com")
        self.page.get_by_label("Ciudad").select_option("Ensenada")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text(
            "NombreClienteee")).to_be_visible()
        expect(self.page.get_by_text(
            "542215552323")).to_be_visible()
        expect(self.page.get_by_text(
            "email3@vetsoft.com")).to_be_visible()
        expect(self.page.get_by_text(
            "Ensenada")).to_be_visible()
