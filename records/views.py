from django.http import JsonResponse
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, permissions
from fpdf import FPDF
from records.fullSerializers import UpdateRecordSerializer, CreateRecordSerializer, FullRecordSerializer
from shared.mixins import DynamicSerializersMixin
from records.models import Records
from rest_framework.decorators import action
from records.serializers import RecordSerializer
from shared.permissions import IsOwner
from django.http import FileResponse


@extend_schema_view(
    list=extend_schema(description='Get paginated list of records.'),
    update=extend_schema(description='Update record data.'),
    partial_update=extend_schema(description='Partially update record data.'),
    destroy=extend_schema(description='Delete a record.'),
    create=extend_schema(description='Create a new record.'),
)
class RecordViewSet(DynamicSerializersMixin, viewsets.ModelViewSet):
    queryset = Records.objects.all()
    serializer_class = RecordSerializer
    serializer_classes_by_action = {
        'update': UpdateRecordSerializer,
        'create': CreateRecordSerializer,
        'partial_update': UpdateRecordSerializer,
        'get_object': FullRecordSerializer,
    }

    permission_classes_by_action = {
        'create': (permissions.IsAuthenticated,),
        'update': (permissions.IsAdminUser | IsOwner,),
        'partial_update': (permissions.IsAdminUser | IsOwner,),
        'destroy': (permissions.IsAdminUser | IsOwner,),
    }

    @action(methods=["get"], detail=False, url_path='charts', url_name="charts")
    def charts(self, arg):
        labels = []
        data = []
        queryset = Records.objects.only('blood_glucose', 'created_date')
        print(queryset)
        for record in queryset:
            labels.append(record.phasesDay.name)
            data.append(record.blood_glucose)

        return JsonResponse(data={
            'data': data,
            'labels': labels,
        })

    @action(methods=["get"], detail=False, url_path='report', url_name="report")
    def report(self, arg):
        data = []

        # Query
        queryset = Records.objects.all()
        for record in list(queryset):
            data.append(record)

        # PDF
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(40, 10, 'Glucose reports:', 0, 1)
        pdf.cell(40, 10, '', 0, 1)
        pdf.line(10, 30, 200, 30)

        # Table
        line_height = pdf.font_size * 1.5
        col_width = pdf.epw / 6

        # Headers
        pdf.set_font('helvetica', 'B', 11)
        pdf.line(10, 38, 200, 38)
        lista = ['Food name', 'Blood glucose', 'Rations', 'Unities', 'Phase day', 'Date']
        for item in lista:
            pdf.multi_cell(col_width, line_height, item, border=0, ln=3)

        # Data
        pdf.set_font('helvetica', '', 10)
        pdf.ln(line_height)
        pdf.line(10, 38, 200, 38)
        for record in data:
            for food in list(record.foods.all()):
                foodN = (str(food.name)[:13] + '...') if len(str(food.name)) > 13 else str(food.name)
                lista = [foodN, str(round(record.blood_glucose)), str(round(food.hc_rations)), str("AQUI FALTA ALGO, EL UNITY"),
                         str(record.phasesDay.name), str(record.phasesDay.created_at.strftime('%m/%d/%y, %H:%M'))]
                for item in lista:
                    pdf.multi_cell(col_width, line_height, item, border=0, ln=3)
                pdf.ln(line_height)

        # Output
        pdf.output('report.pdf', 'F')
        return FileResponse(open('report.pdf', 'rb'), as_attachment=True, content_type='application/pdf')
