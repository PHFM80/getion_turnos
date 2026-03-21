from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from empresas.models import Empresa, Rubro
from geo.models import Localidad, Pais, Provincia
from servicios.models import ServicioBase
from suscripciones.models import Pago, Plan, Suscripcion


def apply_bootstrap_styles(form):
    for name, field in form.fields.items():
        widget = field.widget
        widget_classes = widget.attrs.get("class", "")

        if isinstance(widget, forms.CheckboxInput):
            base_class = "form-check-input"
        elif isinstance(widget, forms.Select):
            base_class = "form-select"
        else:
            base_class = "form-control"

        if form.is_bound and name in form.errors:
            base_class = f"{base_class} is-invalid"

        widget.attrs["class"] = f"{widget_classes} {base_class}".strip()

        if isinstance(widget, forms.Textarea):
            widget.attrs.setdefault("rows", 3)


class RubroForm(forms.ModelForm):
    class Meta:
        model = Rubro
        fields = ["nombre"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if Rubro.objects.filter(nombre__iexact=nombre).exists():
            raise ValidationError("Ya existe un rubro con ese nombre.")
        return nombre


class PaisForm(forms.ModelForm):
    class Meta:
        model = Pais
        fields = ["nombre", "codigo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if Pais.objects.filter(nombre__iexact=nombre).exists():
            raise ValidationError("Ya existe un pais con ese nombre.")
        return nombre


class ProvinciaForm(forms.ModelForm):
    class Meta:
        model = Provincia
        fields = ["nombre", "pais"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get("nombre")
        pais = cleaned_data.get("pais")
        if nombre and pais:
            existe = Provincia.objects.filter(nombre__iexact=nombre.strip(), pais=pais)
            if existe.exists():
                self.add_error("nombre", "Ya existe una provincia con ese nombre en el pais seleccionado.")
        return cleaned_data


class LocalidadForm(forms.ModelForm):
    class Meta:
        model = Localidad
        fields = ["nombre", "provincia"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get("nombre")
        provincia = cleaned_data.get("provincia")
        if nombre and provincia:
            existe = Localidad.objects.filter(nombre__iexact=nombre.strip(), provincia=provincia)
            if existe.exists():
                self.add_error("nombre", "Ya existe una localidad con ese nombre en la provincia seleccionada.")
        return cleaned_data


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ["nombre", "limite_simultaneo", "precio_mensual", "precio_anual"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        existe = Plan.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)
        if existe.exists():
            raise ValidationError("Ya existe un plan con ese nombre.")
        return nombre

    def clean(self):
        cleaned_data = super().clean()
        precio_mensual = cleaned_data.get("precio_mensual")
        precio_anual = cleaned_data.get("precio_anual")
        limite_simultaneo = cleaned_data.get("limite_simultaneo")

        if precio_mensual is not None and precio_mensual < 0:
            self.add_error("precio_mensual", "El precio mensual no puede ser negativo.")
        if precio_anual is not None and precio_anual < 0:
            self.add_error("precio_anual", "El precio anual no puede ser negativo.")
        if limite_simultaneo is not None and limite_simultaneo == 0:
            self.add_error("limite_simultaneo", "Debe ser mayor a cero o vacio para ilimitado.")
        return cleaned_data


class ServicioBaseForm(forms.ModelForm):
    class Meta:
        model = ServicioBase
        fields = ["nombre", "rubro"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nombre"].label = "Nombre del nuevo servicio base"
        self.fields["rubro"].label = "Rubro"
        apply_bootstrap_styles(self)

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get("nombre")
        rubro = cleaned_data.get("rubro")
        if nombre and rubro:
            existe = ServicioBase.objects.filter(nombre__iexact=nombre.strip(), rubro=rubro)
            if existe.exists():
                self.add_error("nombre", "Ya existe un servicio base con ese nombre para el rubro seleccionado.")
        return cleaned_data


class SuscripcionForm(forms.ModelForm):
    class Meta:
        model = Suscripcion
        fields = ["empresa", "plan", "periodicidad", "activa", "fecha_inicio", "fecha_vencimiento"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_vencimiento": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)

    def clean(self):
        cleaned_data = super().clean()
        empresa = cleaned_data.get("empresa")
        activa = cleaned_data.get("activa")
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_vencimiento = cleaned_data.get("fecha_vencimiento")

        if fecha_inicio and fecha_vencimiento and fecha_vencimiento < fecha_inicio:
            self.add_error("fecha_vencimiento", "La fecha de vencimiento debe ser posterior a la fecha de inicio.")

        if empresa and activa:
            existe = Suscripcion.objects.filter(empresa=empresa, activa=True)
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)
            if existe.exists():
                self.add_error("empresa", "La empresa ya tiene una suscripcion activa.")

        return cleaned_data


class SuscripcionEditForm(forms.ModelForm):
    class Meta:
        model = Suscripcion
        fields = ["plan", "periodicidad", "activa"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["nombre", "telefono", "calle", "numero", "pais", "provincia", "localidad", "rubro", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["telefono"].widget.attrs.update(
            {
                "inputmode": "numeric",
                "pattern": r"^\+?\d+$",
                "data-phone-input": "true",
            }
        )
        apply_bootstrap_styles(self)

    def clean_telefono(self):
        telefono_raw = self.cleaned_data["telefono"].strip()
        digits = "".join(ch for ch in telefono_raw if ch.isdigit())
        if not digits:
            raise ValidationError("El telefono debe contener solo numeros.")

        pais = self.cleaned_data.get("pais")
        codigo = None
        if pais and pais.codigo:
            codigo = "".join(ch for ch in pais.codigo if ch.isdigit())
        if not codigo:
            codigo = "54"

        numero = digits.lstrip("0")
        if numero.startswith(codigo):
            telefono = f"+{numero}"
        else:
            telefono = f"+{codigo}{numero}"

        if not (10 <= len(telefono.replace("+", "")) <= 15):
            raise ValidationError("El telefono debe tener entre 10 y 15 digitos.")

        existe = Empresa.objects.filter(telefono__iexact=telefono)
        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)
        if existe.exists():
            raise ValidationError("Ya existe una empresa con ese telefono.")
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        pais = cleaned_data.get("pais")
        provincia = cleaned_data.get("provincia")
        localidad = cleaned_data.get("localidad")

        if pais and provincia and provincia.pais_id != pais.id:
            self.add_error("provincia", "La provincia no pertenece al pais seleccionado.")

        if provincia and localidad and localidad.provincia_id != provincia.id:
            self.add_error("localidad", "La localidad no pertenece a la provincia seleccionada.")

        return cleaned_data


class EmpresaCreateForm(EmpresaForm):
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.order_by("nombre"),
        required=True,
        empty_label="Selecciona un plan",
    )
    periodicidad = forms.ChoiceField(
        choices=Suscripcion.PERIODO_CHOICES,
        initial=Suscripcion.PERIODO_MENSUAL,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)


class UsuarioEmpresaCreateForm(forms.Form):
    rol = forms.ChoiceField(choices=[
        ("dueno", "Dueño"),
        ("empleado", "Empleado"),
    ])
    email = forms.EmailField()
    nombre = forms.CharField(max_length=150)
    apellido = forms.CharField(max_length=150)
    dni = forms.CharField(max_length=20)
    telefono = forms.CharField(max_length=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dni"].widget.attrs.update(
            {"inputmode": "numeric", "pattern": r"\d{7,8}", "maxlength": "8"}
        )
        self.fields["telefono"].widget.attrs.update(
            {"inputmode": "numeric", "pattern": r"\d{10,15}", "maxlength": "15"}
        )
        self.fields["email"].widget.attrs.update(
            {"autocomplete": "email"}
        )
        apply_bootstrap_styles(self)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        user_model = get_user_model()
        if user_model.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un usuario con ese email.")
        return email

    def clean_dni(self):
        dni = self.cleaned_data["dni"].strip()
        if not dni.isdigit() or len(dni) not in (7, 8):
            raise ValidationError("El DNI debe tener 7 u 8 numeros.")
        user_model = get_user_model()
        if user_model.objects.filter(dni__iexact=dni).exists():
            raise ValidationError("Ya existe un usuario con ese DNI.")
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if not telefono.isdigit():
            raise ValidationError("El telefono debe contener solo numeros.")
        if not (10 <= len(telefono) <= 15):
            raise ValidationError("El telefono debe tener entre 10 y 15 numeros.")
        user_model = get_user_model()
        if user_model.objects.filter(telefono__iexact=telefono).exists():
            raise ValidationError("Ya existe un usuario con ese telefono.")
        return telefono


class UsuarioEmpresaEditForm(forms.Form):
    rol = forms.ChoiceField(choices=[
        ("dueno", "Dueño"),
        ("empleado", "Empleado"),
    ])
    email = forms.EmailField()
    nombre = forms.CharField(max_length=150)
    apellido = forms.CharField(max_length=150)
    dni = forms.CharField(max_length=20)
    telefono = forms.CharField(max_length=30)

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance", None)
        super().__init__(*args, **kwargs)
        self.fields["dni"].widget.attrs.update(
            {"inputmode": "numeric", "pattern": r"\d{7,8}", "maxlength": "8"}
        )
        self.fields["telefono"].widget.attrs.update(
            {"inputmode": "numeric", "pattern": r"\d{10,15}", "maxlength": "15"}
        )
        self.fields["email"].widget.attrs.update(
            {"autocomplete": "email"}
        )
        apply_bootstrap_styles(self)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        user_model = get_user_model()
        existe = user_model.objects.filter(email__iexact=email)
        if self.user_instance:
            existe = existe.exclude(pk=self.user_instance.pk)
        if existe.exists():
            raise ValidationError("Ya existe un usuario con ese email.")
        return email

    def clean_dni(self):
        dni = self.cleaned_data["dni"].strip()
        if not dni.isdigit() or len(dni) not in (7, 8):
            raise ValidationError("El DNI debe tener 7 u 8 numeros.")
        user_model = get_user_model()
        existe = user_model.objects.filter(dni__iexact=dni)
        if self.user_instance:
            existe = existe.exclude(pk=self.user_instance.pk)
        if existe.exists():
            raise ValidationError("Ya existe un usuario con ese DNI.")
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if not telefono.isdigit():
            raise ValidationError("El telefono debe contener solo numeros.")
        if not (10 <= len(telefono) <= 15):
            raise ValidationError("El telefono debe tener entre 10 y 15 numeros.")
        user_model = get_user_model()
        existe = user_model.objects.filter(telefono__iexact=telefono)
        if self.user_instance:
            existe = existe.exclude(pk=self.user_instance.pk)
        if existe.exists():
            raise ValidationError("Ya existe un usuario con ese telefono.")
        return telefono


class PagoForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.suscripcion = kwargs.pop("suscripcion", None)
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)

    def clean(self):
        cleaned_data = super().clean()
        if not self.suscripcion:
            raise ValidationError("La empresa no tiene suscripcion para registrar pagos.")
        periodo = self.suscripcion.periodicidad
        if not periodo:
            return cleaned_data

        if periodo == Suscripcion.PERIODO_MENSUAL:
            today = timezone.now().date()
            ultimo_pago = (
                Pago.objects.filter(suscripcion=self.suscripcion)
                .order_by("-fecha_pago", "-id")
                .first()
            )
            if (
                ultimo_pago
                and ultimo_pago.periodo == Suscripcion.PERIODO_ANUAL
                and self.suscripcion.fecha_vencimiento
            ):
                dias_para_vencer = (self.suscripcion.fecha_vencimiento - today).days
                if dias_para_vencer > 7:
                    raise ValidationError(
                        "No se puede registrar un pago mensual mientras el anual no este proximo a vencer (<= 7 dias)."
                    )
        return cleaned_data
