from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_plantilla_layout'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImagenHero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(help_text='Recomendado 1920×1080 px o superior', upload_to='hero/')),
                ('orden', models.PositiveSmallIntegerField(default=0, help_text='Menor número aparece primero')),
                ('activo', models.BooleanField(default=True)),
                ('configuracion', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='imagenes_hero',
                    to='usuarios.configuracionestudio',
                )),
            ],
            options={
                'verbose_name': 'Imagen Hero',
                'verbose_name_plural': 'Imágenes Hero',
                'ordering': ['orden', 'pk'],
            },
        ),
    ]
