from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0010_logo_navbar_logo_hero'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='banco',
            field=models.CharField(blank=True, max_length=60, verbose_name='Banco', help_text='Ej: BBVA, Banamex, Santander'),
        ),
        migrations.AddField(
            model_name='perfil',
            name='titular_cuenta',
            field=models.CharField(blank=True, max_length=120, verbose_name='Titular de la cuenta'),
        ),
        migrations.AddField(
            model_name='perfil',
            name='clabe',
            field=models.CharField(blank=True, max_length=30, verbose_name='CLABE / Número de cuenta', help_text='CLABE interbancaria o número de tarjeta'),
        ),
    ]
