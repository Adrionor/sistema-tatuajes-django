from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0005_cotizacion_notas_cliente'),
    ]

    operations = [
        # Make the legacy single-image field optional
        migrations.AlterField(
            model_name='cotizacion',
            name='imagen_referencia',
            field=models.ImageField(blank=True, null=True, upload_to='referencias/'),
        ),
        # New model for multiple reference images
        migrations.CreateModel(
            name='ReferenciaImagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='referencias/')),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                (
                    'cotizacion',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='referencias',
                        to='cotizaciones.cotizacion',
                    ),
                ),
            ],
            options={
                'ordering': ['orden'],
            },
        ),
    ]
