# Generated by Django 3.1.2 on 2020-12-05 17:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20201205_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='texttoasciitype',
            name='multi_line_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ImageToASCIIOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('columns', models.CharField(max_length=64)),
                ('brightness', models.CharField(max_length=64)),
                ('contrast', models.CharField(max_length=64)),
                ('image_to_ascii_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='app.imagetoasciitype')),
            ],
        ),
    ]
