from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0006_skin_idioma'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracionestudio',
            name='plantilla_layout',
            field=models.CharField(
                choices=[
                    ('clasico', 'Clásico'),
                    ('revista', 'Revista'),
                    ('minimal', 'Minimal'),
                    ('impacto', 'Impacto'),
                    ('mosaico', 'Mosaico'),
                ],
                default='clasico',
                help_text='Disposición de las páginas públicas (landing, artistas, perfiles)',
                max_length=20,
                verbose_name='Plantilla de diseño',
            ),
        ),
    ]
