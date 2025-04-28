from django.urls import reverse

# agregamos un nuevo contexto para el navbar de mascotas
links = [
    {"label": "Home", "href": reverse("home"), "icon": "bi bi-house-door"},
    {"label": "Clientes", "href": reverse(
        "clients_repo"), "icon": "bi bi-people"},
    {"label": "Proveedor", "href": reverse(
        "providers_repo"), "icon": "bi bi-people"},
    {"label": "Productos", "href": reverse(
        "products_repo"), "icon": "bi bi-box"},
    {"label": "Veterinario", "href": reverse(
        "vets_repo"), "icon": "bi bi-person-vcard-fill"},
    {"label": "Medicamentos", "href": reverse(
        "medicines_repo"), "icon": "bi bi-capsule-pill"},  # Nuevo enlace para medicamentos
    {"label": "Mascotas", "href": reverse(
        "pets_repo"), "icon": "bi bi-heart-fill"},

]


def navbar(request):
    """Genera los enlaces de navegación y agrega la clase "active" al enlace correspondiente basado en la ruta actual"""
    def add_active(link):
        copy = link.copy()

        if copy["href"] == "/":
            copy["active"] = request.path == "/"
        else:
            copy["active"] = request.path.startswith(copy.get("href", ""))

        return copy

    return {"links": map(add_active, links)}
