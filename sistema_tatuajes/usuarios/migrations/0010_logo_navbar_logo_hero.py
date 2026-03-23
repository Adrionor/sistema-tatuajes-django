from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0009_anuncio_estudio_configuracionestudio_subdominio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionestudio',
            name='logo_navbar',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='logos/',
                verbose_name='Logo del navbar',
                help_text='Se muestra en la barra de navegación en lugar del nombre. PNG transparente recomendado.',
            ),
        ),
        migrations.AddField(
            model_name='configuracionestudio',
            name='logo_hero',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='logos/',
                verbose_name='Logo del hero',
                help_text='Se muestra en el hero de la landing en lugar de la tipografía.',
            ),
        ),
    ]
