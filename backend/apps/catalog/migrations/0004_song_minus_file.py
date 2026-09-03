from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_album_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="song",
            name="minus_file",
            field=models.FileField(
                blank=True,
                help_text="Необязательно. Минусовка трека. Если загружена, на сайте появится кнопка «Минус».",
                null=True,
                upload_to="songs/minus/",
                verbose_name="Минус",
            ),
        ),
    ]
