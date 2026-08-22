from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="song",
            name="lyrics",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="Текст песни",
            ),
        ),
        migrations.AlterField(
            model_name="song",
            name="duration_seconds",
            field=models.IntegerField(
                default=0,
                help_text="Определяется автоматически из аудиофайла.",
                verbose_name="Продолжительность (сек.)",
            ),
        ),
    ]
