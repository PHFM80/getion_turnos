from django import forms
from django.core.exceptions import ValidationError

from empresas.models import Rubro
from geo.models import Localidad, Pais, Provincia
from servicios.models import ServicioBase
from suscripciones.models import Plan, Suscripcion


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
        fields = ["nombre"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_styles(self)

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if Plan.objects.filter(nombre__iexact=nombre).exists():
            raise ValidationError("Ya existe un plan con ese nombre.")
        return nombre


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
        fields = ["empresa", "plan", "activa", "fecha_inicio", "fecha_vencimiento"]
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
