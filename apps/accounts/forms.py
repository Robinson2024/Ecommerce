"""
Forms para la app accounts.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from .models import User, UserProfile, Address


class CustomUserCreationForm(UserCreationForm):
    """Form personalizado para crear usuarios."""
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


class CustomUserChangeForm(UserChangeForm):
    """Form personalizado para cambiar usuarios."""
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


class UserProfileForm(forms.ModelForm):
    """Form para el perfil del usuario."""
    
    # Campos del usuario
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Teléfono')
    birth_date = forms.DateField(
        required=False, 
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=[('', 'Seleccionar')] + User.gender_choices,
        required=False,
        label='Género'
    )
    newsletter_subscription = forms.BooleanField(
        required=False,
        label='Suscribirse al newsletter'
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'document_type', 'document_number', 'occupation', 
            'company', 'preferred_language', 'timezone',
            'bio', 'website', 'instagram', 'twitter'
        ]
        
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'website': forms.URLInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Poblar campos del usuario si existe la instancia
        if self.instance and self.instance.user:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.phone
            self.fields['birth_date'].initial = user.birth_date
            self.fields['gender'].initial = user.gender
            self.fields['newsletter_subscription'].initial = user.newsletter_subscription
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>Información Personal</h4>'),
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6'),
                Column('phone', css_class='form-group col-md-6'),
            ),
            Row(
                Column('birth_date', css_class='form-group col-md-6'),
                Column('gender', css_class='form-group col-md-6'),
            ),
            
            HTML('<h4 class="mt-4">Información Profesional</h4>'),
            Row(
                Column('document_type', css_class='form-group col-md-4'),
                Column('document_number', css_class='form-group col-md-8'),
            ),
            Row(
                Column('occupation', css_class='form-group col-md-6'),
                Column('company', css_class='form-group col-md-6'),
            ),
            
            HTML('<h4 class="mt-4">Preferencias</h4>'),
            Row(
                Column('preferred_language', css_class='form-group col-md-6'),
                Column('timezone', css_class='form-group col-md-6'),
            ),
            Field('newsletter_subscription', css_class='form-check'),
            
            HTML('<h4 class="mt-4">Redes Sociales</h4>'),
            'bio',
            Row(
                Column('website', css_class='form-group col-md-6'),
                Column('instagram', css_class='form-group col-md-3'),
                Column('twitter', css_class='form-group col-md-3'),
            ),
            
            Submit('submit', 'Guardar Cambios', css_class='btn btn-primary')
        )
    
    def save(self, commit=True):
        """Guardar tanto el perfil como los datos del usuario."""
        profile = super().save(commit=False)
        
        if profile.user:
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone = self.cleaned_data['phone']
            user.birth_date = self.cleaned_data['birth_date']
            user.gender = self.cleaned_data['gender']
            user.newsletter_subscription = self.cleaned_data['newsletter_subscription']
            
            if commit:
                user.save()
        
        if commit:
            profile.save()
        
        return profile


class AddressForm(forms.ModelForm):
    """Form para direcciones."""
    
    class Meta:
        model = Address
        fields = [
            'title', 'first_name', 'last_name', 'phone',
            'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'is_default_billing',
            'is_default_shipping', 'delivery_instructions'
        ]
        
        widgets = {
            'delivery_instructions': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>Información de Contacto</h4>'),
            'title',
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
            ),
            'phone',
            
            HTML('<h4 class="mt-4">Dirección</h4>'),
            'address_line_1',
            'address_line_2',
            Row(
                Column('city', css_class='form-group col-md-4'),
                Column('state', css_class='form-group col-md-4'),
                Column('postal_code', css_class='form-group col-md-4'),
            ),
            'country',
            
            HTML('<h4 class="mt-4">Configuraciones</h4>'),
            Row(
                Column(
                    Field('is_default_billing', css_class='form-check'),
                    css_class='col-md-6'
                ),
                Column(
                    Field('is_default_shipping', css_class='form-check'),
                    css_class='col-md-6'
                ),
            ),
            
            'delivery_instructions',
            
            Submit('submit', 'Guardar Dirección', css_class='btn btn-primary')
        )
