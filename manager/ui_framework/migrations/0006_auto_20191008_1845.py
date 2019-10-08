# Generated by Django 2.2.6 on 2019-10-08 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ui_framework', '0005_auto_20191008_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workspaceview',
            name='view',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workspace_views', to='ui_framework.View'),
        ),
        migrations.AlterField(
            model_name='workspaceview',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workspace_views', to='ui_framework.Workspace'),
        ),
    ]
